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

UNIDADES = ["kg", "g", "lt", "ml", "und", "paquete", "caja"]

TIPOS_MOVIMIENTO = {
    "entrada":  "📥 Entrada",
    "salida":   "📤 Salida",
    "ajuste":   "🔧 Ajuste",
    "merma":    "🗑️ Merma / Desperdicio",
}


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


def obtener_ingrediente(ingredient_id: str) -> dict | None:
    supabase = get_supabase()
    resultado = (
        supabase.table("ingredients")
        .select("*")
        .eq("id", ingredient_id)
        .limit(1)
        .execute()
        .data
    )
    return resultado[0] if resultado else None


def obtener_ingredientes_bajo_minimo(restaurant_id: str) -> list:
    """Ingredientes con stock_current <= stock_min (incluye sin stock)."""
    ingredientes = obtener_ingredientes(restaurant_id)
    return [
        i for i in ingredientes
        if float(i["stock_current"]) <= float(i["stock_min"])
    ]


def crear_ingrediente(restaurant_id: str, nombre: str, unidad: str,
                      stock_min: float, costo_unitario: float,
                      categoria: str) -> dict:
    supabase = get_supabase()
    return (
        supabase.table("ingredients")
        .insert({
            "restaurant_id": restaurant_id,
            "name": nombre,
            "unit": unidad,
            "stock_current": 0.0,
            "stock_min": stock_min,
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
      'entrada'  → suma cantidad al stock (puede actualizar costo_per_unit)
      'salida'   → resta cantidad al stock
      'merma'    → igual que salida pero etiquetado como desperdicio
      'ajuste'   → cantidad es el NUEVO stock total (conteo físico)
    """
    supabase = get_supabase()

    ingrediente = (
        supabase.table("ingredients")
        .select("stock_current, cost_per_unit")
        .eq("id", ingredient_id)
        .execute()
        .data[0]
    )
    stock_actual = float(ingrediente["stock_current"])

    if tipo == "entrada":
        delta = cantidad
        nuevo_stock = stock_actual + cantidad
    elif tipo in ("salida", "merma"):
        delta = -cantidad
        nuevo_stock = max(0.0, stock_actual - cantidad)
    else:  # ajuste
        delta = cantidad - stock_actual
        nuevo_stock = cantidad

    # Insertar movimiento
    mov = (
        supabase.table("stock_movements")
        .insert({
            "restaurant_id": restaurant_id,
            "ingredient_id": ingredient_id,
            "type": tipo,
            "quantity": delta,
            "reason": motivo or None,
            "cost_per_unit": costo_unitario,
        })
        .execute()
        .data[0]
    )

    # Actualizar stock y costo si viene con precio
    update_data: dict = {"stock_current": nuevo_stock}
    if tipo == "entrada" and costo_unitario and costo_unitario > 0:
        update_data["cost_per_unit"] = costo_unitario

    supabase.table("ingredients").update(update_data).eq("id", ingredient_id).execute()

    return mov


def obtener_movimientos(restaurant_id: str,
                        ingredient_id: str | None = None,
                        limit: int = 100) -> list:
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
    """Calcula el valor monetario total del inventario actual."""
    ingredientes = obtener_ingredientes(restaurant_id)
    return sum(
        float(i["stock_current"]) * float(i["cost_per_unit"])
        for i in ingredientes
    )
