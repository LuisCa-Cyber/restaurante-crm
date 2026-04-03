# database/orders.py — Gestión de órdenes y sus items

from datetime import datetime, timezone
from database.supabase_client import get_supabase


def crear_orden(restaurant_id: str, table_id: str, table_name: str,
                waiter_id: str, waiter_name: str) -> dict:
    """Crea una nueva orden abierta para una mesa."""
    supabase = get_supabase()
    return (
        supabase.table("orders")
        .insert({
            "restaurant_id": restaurant_id,
            "table_id": table_id,
            "table_name": table_name,
            "waiter_id": waiter_id,
            "waiter_name": waiter_name,
            "status": "open",
            "total": 0,
        })
        .execute()
        .data[0]
    )


def obtener_orden_abierta_de_mesa(table_id: str) -> dict | None:
    """Retorna la orden abierta de una mesa, o None si no hay."""
    supabase = get_supabase()
    resultado = (
        supabase.table("orders")
        .select("*")
        .eq("table_id", table_id)
        .eq("status", "open")
        .limit(1)
        .execute()
        .data
    )
    return resultado[0] if resultado else None


def obtener_ordenes_abiertas(restaurant_id: str) -> list:
    """Retorna todas las órdenes abiertas del restaurante."""
    supabase = get_supabase()
    return (
        supabase.table("orders")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .eq("status", "open")
        .order("created_at")
        .execute()
        .data
    )


def obtener_items_orden(order_id: str) -> list:
    """Retorna todos los items de una orden."""
    supabase = get_supabase()
    return (
        supabase.table("order_items")
        .select("*")
        .eq("order_id", order_id)
        .order("created_at")
        .execute()
        .data
    )


def agregar_items(order_id: str, items: list):
    """
    Agrega items a una orden existente.
    items: [{"menu_item_id": str, "menu_item_name": str, "unit_price": float,
             "quantity": int, "notes": str (opcional)}]
    """
    supabase = get_supabase()
    registros = [
        {
            "order_id": order_id,
            "menu_item_id": item["menu_item_id"],
            "menu_item_name": item["menu_item_name"],
            "unit_price": item["unit_price"],
            "quantity": item["quantity"],
            "notes": item.get("notes") or None,
            "delivered": False,
        }
        for item in items
    ]
    supabase.table("order_items").insert(registros).execute()
    _recalcular_total(order_id)


def marcar_item_entregado(item_id: str, entregado: bool):
    supabase = get_supabase()
    supabase.table("order_items").update({"delivered": entregado}).eq("id", item_id).execute()


def _recalcular_total(order_id: str):
    """Recalcula y guarda el total de la orden sumando todos sus items."""
    supabase = get_supabase()
    items = obtener_items_orden(order_id)
    total = sum(i["unit_price"] * i["quantity"] for i in items)
    supabase.table("orders").update({"total": total}).eq("id", order_id).execute()


def cerrar_orden(order_id: str) -> dict:
    """Cierra la orden: registra fecha de cierre y marca como cerrada."""
    supabase = get_supabase()
    _recalcular_total(order_id)
    return (
        supabase.table("orders")
        .update({
            "status": "closed",
            "closed_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", order_id)
        .execute()
        .data[0]
    )


def obtener_ventas(restaurant_id: str, desde: str, hasta: str) -> list:
    """
    Retorna órdenes cerradas en un rango de fechas.
    desde / hasta: strings en formato 'YYYY-MM-DD'
    """
    supabase = get_supabase()
    return (
        supabase.table("orders")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .eq("status", "closed")
        .gte("closed_at", desde)
        .lte("closed_at", hasta + "T23:59:59")
        .order("closed_at")
        .execute()
        .data
    )
