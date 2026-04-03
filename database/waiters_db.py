# database/waiters_db.py — Gestión de meseros del restaurante

from database.supabase_client import get_supabase


def obtener_meseros(restaurant_id: str) -> list:
    supabase = get_supabase()
    return (
        supabase.table("waiters")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .eq("active", True)
        .order("name")
        .execute()
        .data
    )


def crear_mesero(restaurant_id: str, nombre: str) -> dict:
    supabase = get_supabase()
    return (
        supabase.table("waiters")
        .insert({"restaurant_id": restaurant_id, "name": nombre, "active": True})
        .execute()
        .data[0]
    )


def toggle_mesero_activo(waiter_id: str, activo: bool):
    supabase = get_supabase()
    supabase.table("waiters").update({"active": activo}).eq("id", waiter_id).execute()


def eliminar_mesero(waiter_id: str):
    supabase = get_supabase()
    supabase.table("waiters").delete().eq("id", waiter_id).execute()
