# database/stock_db.py — Gestión de inventario / stock

from database.supabase_client import get_supabase

CATEGORIAS_INSUMOS = [
    "Carnes y mariscos",
    "Verduras y hortalizas",
    "Lácteos y huevos",
    "Granos y legumbres",
    "Bebidas",
    "Condimentos y salsas",
    "Otros",
]

UNIDADES = ["kg", "g", "lt", "ml", "und", "libra", "paquete", "caja"]


def nivel_alerta(ingrediente: dict) -> str:
    """
    Retorna el nivel de alerta según dos umbrales:
      'rojo'     → stock <= stock_critical
      'amarillo' → stock <= stock_min
      'verde'    → stock > stock_min
    """
    stock = float(ingrediente["stock_current"])
    critico = float(ingrediente.get("stock_critical") or 0)
    minimo  = float(ingrediente.get("stock_min") or 0)

    if stock <= critico:
        return "rojo"
    if stock <= minimo:
        return "amarillo"
    return "verde"


# ── Ingredientes ───────────────────────────────────────────────────────────────

def obtener_ingredientes(restaurant_id: str) -> list:
    supabase = get_supabase()
    return (
        supabase.table("ingredients")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .order("category")
        .order("name")
        .execute()
        .data
    )


def crear_ingrediente(restaurant_id: str, nombre: str, unidad: str,
                      stock_min: float, stock_critical: float,
                      costo_unitario: float, categoria: str) -> dict:
    supabase = get_supabase()
    return (
        supabase.table("ingredients")
        .insert({
            "restaurant_id": restaurant_id,
            "name": nombre,
            "unit": unidad,
            "stock_current": 0.0,
            "stock_min": stock_min,
            "stock_critical": stock_critical,
            "cost_per_unit": costo_unitario,
            "category": categoria,
        })
        .execute()
        .data[0]
    )


def actualizar_ingrediente(ingredient_id: str, data: dict):
    supabase = get_supabase()
    supabase.table("ingredients").update(data).eq("id", ingredient_id).execute()


def eliminar_ingrediente(ingredient_id: str):
    supabase = get_supabase()
    supabase.table("ingredients").delete().eq("id", ingredient_id).execute()


# ── Movimientos ────────────────────────────────────────────────────────────────

def registrar_movimiento(restaurant_id: str, ingredient_id: str,
                         tipo: str, cantidad: float, motivo: str,
                         costo_unitario: float | None = None) -> dict:
    """
    Registra un movimiento y actualiza stock_current.

    tipo:
      'entrada'  → suma cantidad. Si llega precio, actualiza cost_per_unit.
      'salida'   → resta cantidad. Calcula costo proporcional automáticamente.
      'merma'    → igual que salida. Calcula costo proporcional.
      'ajuste'   → cantidad es el NUEVO stock total (conteo físico).
    """
    supabase = get_supabase()

    ingrediente = (
        supabase.table("ingredients")
        .select("stock_current, cost_per_unit")
        .eq("id", ingredient_id)
        .execute()
        .data[0]
    )
    stock_actual   = float(ingrediente["stock_current"])
    costo_actual   = float(ingrediente["cost_per_unit"])

    if tipo == "entrada":
        delta      = cantidad
        nuevo_stock = stock_actual + cantidad
        costo_mov  = costo_unitario  # puede ser None si no se ingresó precio

    elif tipo in ("salida", "merma"):
        delta       = -cantidad
        nuevo_stock = max(0.0, stock_actual - cantidad)
        # Costo proporcional: (cantidad_salida × costo_unitario_actual)
        costo_mov   = costo_actual  # registramos el costo/u vigente al momento

    else:  # ajuste
        delta       = cantidad - stock_actual
        nuevo_stock = cantidad
        costo_mov   = None

    mov = (
        supabase.table("stock_movements")
        .insert({
            "restaurant_id": restaurant_id,
            "ingredient_id": ingredient_id,
            "type": tipo,
            "quantity": delta,
            "reason": motivo or None,
            "cost_per_unit": costo_mov,
        })
        .execute()
        .data[0]
    )

    # Actualizar stock; si es entrada con precio, actualizar costo también
    update_data: dict = {"stock_current": nuevo_stock}
    if tipo == "entrada" and costo_unitario and costo_unitario > 0:
        update_data["cost_per_unit"] = costo_unitario

    supabase.table("ingredients").update(update_data).eq("id", ingredient_id).execute()

    return mov


def obtener_movimientos(restaurant_id: str,
                        ingredient_id: str | None = None,
                        limit: int = 200) -> list:
    supabase = get_supabase()
    query = (
        supabase.table("stock_movements")
        .select("*, ingredients(name, unit)")
        .eq("restaurant_id", restaurant_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if ingredient_id:
        query = query.eq("ingredient_id", ingredient_id)
    return query.execute().data


def valor_total_inventario(restaurant_id: str) -> float:
    ingredientes = obtener_ingredientes(restaurant_id)
    return sum(
        float(i["stock_current"]) * float(i["cost_per_unit"])
        for i in ingredientes
    )


def resumen_costos(restaurant_id: str) -> dict:
    """
    Calcula totales de inversión, consumo y mermas para el dashboard de stock.
    Retorna:
      invertido     → suma de (cantidad_entrada × costo/u) de todas las entradas
      costo_consumo → suma de (|cantidad| × costo/u) de todas las salidas
      costo_merma   → suma de (|cantidad| × costo/u) de todas las mermas
    """
    movs = obtener_movimientos(restaurant_id, limit=2000)
    invertido     = 0.0
    costo_consumo = 0.0
    costo_merma   = 0.0

    for m in movs:
        qty   = abs(float(m["quantity"]))
        cpu   = float(m["cost_per_unit"]) if m.get("cost_per_unit") else 0.0
        if m["type"] == "entrada":
            invertido     += qty * cpu
        elif m["type"] == "salida":
            costo_consumo += qty * cpu
        elif m["type"] == "merma":
            costo_merma   += qty * cpu

    return {
        "invertido":     invertido,
        "costo_consumo": costo_consumo,
        "costo_merma":   costo_merma,
    }
