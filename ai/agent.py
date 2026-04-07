# ai/agent.py — Agente de chat con datos del restaurante (OpenAI GPT-4o-mini)

import json
from datetime import date, timedelta
from openai import OpenAI
from config.settings import get_env
from database.supabase_client import get_supabase


def _client():
    return OpenAI(api_key=get_env("OPENAI_API_KEY"))


# ── Funciones que el agente puede llamar ─────────────────────────────────────

def _rango_fechas(dias: int, fecha_desde: str | None, fecha_hasta: str | None):
    """Retorna (desde_iso, hasta_iso). Fechas exactas tienen prioridad sobre dias."""
    if fecha_desde:
        desde = fecha_desde
    else:
        desde = (date.today() - timedelta(days=dias)).isoformat()
    hasta = fecha_hasta or date.today().isoformat()
    return desde, hasta


def _ventas_resumen(restaurant_id: str, dias: int = 30,
                    fecha_desde: str | None = None, fecha_hasta: str | None = None) -> dict:
    supabase = get_supabase()
    desde, hasta = _rango_fechas(dias, fecha_desde, fecha_hasta)
    rows = (
        supabase.table("orders")
        .select("total, waiter_name, closed_at, table_name")
        .eq("restaurant_id", restaurant_id)
        .eq("status", "closed")
        .gte("closed_at", desde)
        .lte("closed_at", hasta + "T23:59:59")
        .execute()
        .data
    )
    if not rows:
        return {"mensaje": f"No hay ventas entre {desde} y {hasta}."}
    totales = [float(r["total"]) for r in rows]
    return {
        "periodo_desde": desde,
        "periodo_hasta": hasta,
        "total_ventas": sum(totales),
        "mesas_atendidas": len(rows),
        "ticket_promedio": sum(totales) / len(totales),
        "ticket_maximo": max(totales),
        "ticket_minimo": min(totales),
    }


def _top_platos(restaurant_id: str, dias: int = 30, limite: int = 10,
                fecha_desde: str | None = None, fecha_hasta: str | None = None) -> list:
    supabase = get_supabase()
    desde, hasta = _rango_fechas(dias, fecha_desde, fecha_hasta)
    ordenes = (
        supabase.table("orders")
        .select("id")
        .eq("restaurant_id", restaurant_id)
        .eq("status", "closed")
        .gte("closed_at", desde)
        .lte("closed_at", hasta + "T23:59:59")
        .execute()
        .data
    )
    if not ordenes:
        return []
    ids = [o["id"] for o in ordenes]
    items = (
        supabase.table("order_items")
        .select("menu_item_name, quantity")
        .in_("order_id", ids)
        .execute()
        .data
    )
    conteo: dict = {}
    for item in items:
        nombre = item["menu_item_name"]
        conteo[nombre] = conteo.get(nombre, 0) + int(item["quantity"])
    ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    return [{"plato": k, "unidades_vendidas": v} for k, v in ordenado[:limite]]


def _rendimiento_meseros(restaurant_id: str, dias: int = 30,
                         fecha_desde: str | None = None, fecha_hasta: str | None = None) -> list:
    supabase = get_supabase()
    desde, hasta = _rango_fechas(dias, fecha_desde, fecha_hasta)
    rows = (
        supabase.table("orders")
        .select("waiter_name, total")
        .eq("restaurant_id", restaurant_id)
        .eq("status", "closed")
        .gte("closed_at", desde)
        .lte("closed_at", hasta + "T23:59:59")
        .execute()
        .data
    )
    resumen: dict = {}
    for r in rows:
        w = r["waiter_name"] or "Sin asignar"
        if w not in resumen:
            resumen[w] = {"ventas_total": 0.0, "mesas": 0}
        resumen[w]["ventas_total"] += float(r["total"])
        resumen[w]["mesas"] += 1
    resultado = [
        {"mesero": k, "ventas_total": v["ventas_total"], "mesas_atendidas": v["mesas"],
         "ticket_promedio": v["ventas_total"] / v["mesas"]}
        for k, v in resumen.items()
    ]
    return sorted(resultado, key=lambda x: x["ventas_total"], reverse=True)


def _stock_actual(restaurant_id: str) -> dict:
    supabase = get_supabase()
    rows = (
        supabase.table("ingredients")
        .select("name, unit, stock_current, stock_min, stock_critical, cost_per_unit, category")
        .eq("restaurant_id", restaurant_id)
        .execute()
        .data
    )
    criticos, minimos, ok = [], [], []
    valor_total = 0.0
    for r in rows:
        stock = float(r["stock_current"])
        valor_total += stock * float(r["cost_per_unit"])
        entrada = {"nombre": r["name"], "stock": stock, "unidad": r["unit"], "categoria": r["category"]}
        if stock <= float(r["stock_critical"] or 0):
            criticos.append(entrada)
        elif stock <= float(r["stock_min"] or 0):
            minimos.append(entrada)
        else:
            ok.append(entrada)
    return {
        "total_insumos": len(rows),
        "valor_inventario": valor_total,
        "criticos": criticos,
        "en_minimo": minimos,
        "en_buen_estado": len(ok),
    }


def _consumo_stock(restaurant_id: str, dias: int = 30,
                   fecha_desde: str | None = None, fecha_hasta: str | None = None) -> list:
    supabase = get_supabase()
    desde, hasta = _rango_fechas(dias, fecha_desde, fecha_hasta)
    movs = (
        supabase.table("stock_movements")
        .select("type, quantity, cost_per_unit, ingredients(name, unit)")
        .eq("restaurant_id", restaurant_id)
        .gte("created_at", desde)
        .lte("created_at", hasta + "T23:59:59")
        .execute()
        .data
    )
    resumen: dict = {}
    for m in movs:
        nombre = m["ingredients"]["name"] if m.get("ingredients") else "Desconocido"
        unidad = m["ingredients"]["unit"] if m.get("ingredients") else ""
        if nombre not in resumen:
            resumen[nombre] = {"unidad": unidad, "consumido": 0.0, "merma": 0.0,
                               "costo_consumo": 0.0, "costo_merma": 0.0}
        qty = abs(float(m["quantity"]))
        cpu = float(m["cost_per_unit"]) if m.get("cost_per_unit") else 0.0
        if m["type"] == "salida":
            resumen[nombre]["consumido"] += qty
            resumen[nombre]["costo_consumo"] += qty * cpu
        elif m["type"] == "merma":
            resumen[nombre]["merma"] += qty
            resumen[nombre]["costo_merma"] += qty * cpu
    resultado = [{"insumo": k, **v} for k, v in resumen.items() if v["consumido"] > 0 or v["merma"] > 0]
    return sorted(resultado, key=lambda x: x["costo_consumo"], reverse=True)


# ── Definición de herramientas para OpenAI ───────────────────────────────────

_FECHA_PROPS = {
    "dias": {"type": "integer", "description": "Últimos N días. Usar solo si no se especifican fechas exactas. Por defecto 30."},
    "fecha_desde": {"type": "string", "description": "Fecha de inicio en formato YYYY-MM-DD. Usar cuando el usuario mencione una fecha o rango específico."},
    "fecha_hasta": {"type": "string", "description": "Fecha de fin en formato YYYY-MM-DD. Usar junto con fecha_desde."},
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "ventas_resumen",
            "description": "Resumen de ventas: total facturado, mesas atendidas, ticket promedio, máximo y mínimo. Usar fecha_desde/fecha_hasta cuando el usuario pida un rango específico.",
            "parameters": {"type": "object", "properties": _FECHA_PROPS},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_platos",
            "description": "Platos más vendidos en unidades en un período.",
            "parameters": {
                "type": "object",
                "properties": {
                    **_FECHA_PROPS,
                    "limite": {"type": "integer", "description": "Cuántos platos mostrar. Por defecto 10."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rendimiento_meseros",
            "description": "Ventas y mesas atendidas por mesero en un período.",
            "parameters": {"type": "object", "properties": _FECHA_PROPS},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "stock_actual",
            "description": "Estado actual del inventario: insumos críticos, en mínimo, valor total en bodega.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consumo_stock",
            "description": "Qué insumos se han consumido y cuánto ha costado. También muestra mermas/pérdidas.",
            "parameters": {"type": "object", "properties": _FECHA_PROPS},
        },
    },
]

_TOOL_MAP = {
    "ventas_resumen": _ventas_resumen,
    "top_platos": _top_platos,
    "rendimiento_meseros": _rendimiento_meseros,
    "stock_actual": _stock_actual,
    "consumo_stock": _consumo_stock,
}

SYSTEM_PROMPT = """Eres el asistente de inteligencia del restaurante. Tienes acceso a datos reales de ventas, inventario y personal.

Responde siempre en español, de forma clara y directa. Cuando uses datos numéricos, formatea los pesos colombianos con el símbolo 💲 y separadores de miles. Sé conciso pero completo. Si el usuario pregunta algo que no está en tus herramientas, dilo honestamente.

IMPORTANTE: Al final de cada respuesta, agrega siempre una sección corta llamada "📍 ¿Cómo verlo en la app?" donde le explicas al usuario en qué módulo y pestaña puede encontrar esa misma información por su cuenta. Los módulos disponibles son:
- ☀️ Programación del día → activa platos del día y gestiona el menú
- 🏪 Caja y servicio → órdenes activas, pendientes y cierre de cuentas
- 👥 Equipo y mesas → mesas y meseros
- 📦 Stock → inventario, mis insumos e historial de movimientos
- 📊 Dashboards → pestaña "Métricas de ventas" para ventas/meseros, pestaña "Costos de stock" para inventario y mermas
Sé breve en esta sección, máximo 2 líneas."""


def chat(restaurant_id: str, historial: list, mensaje_usuario: str) -> str:
    """
    Recibe el historial de mensajes y el nuevo mensaje del usuario.
    Retorna la respuesta del asistente como string.
    """
    client = _client()
    hoy = date.today().isoformat()

    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nFecha de hoy: {hoy}"}]
    messages += historial
    messages.append({"role": "user", "content": mensaje_usuario})

    # Primera llamada — el modelo puede pedir herramientas
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    # Ejecutar herramientas si las pide
    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            fn_args["restaurant_id"] = restaurant_id
            resultado = _TOOL_MAP[fn_name](**fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(resultado, ensure_ascii=False),
            })
        # Segunda llamada con los resultados
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return response2.choices[0].message.content

    return msg.content
