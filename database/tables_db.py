# database/tables_db.py — Gestión de mesas del restaurante

import re
from database.supabase_client import get_supabase


def _natural_key(mesa: dict):
    """Ordena por nombre con números como enteros (Mesa 2 antes que Mesa 10)."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", mesa["name"])]


def obtener_mesas(restaurant_id: str) -> list:
    supabase = get_supabase()
    mesas = (
        supabase.table("tables")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .execute()
        .data
    )
    return sorted(mesas, key=_natural_key)


def crear_mesa(restaurant_id: str, nombre: str) -> dict:
    supabase = get_supabase()
    return (
        supabase.table("tables")
        .insert({"restaurant_id": restaurant_id, "name": nombre, "status": "available"})
        .execute()
        .data[0]
    )


def eliminar_mesa(mesa_id: str):
    supabase = get_supabase()
    supabase.table("tables").delete().eq("id", mesa_id).execute()


def actualizar_estado_mesa(table_id: str, status: str):
    """status: 'available' | 'occupied'"""
    supabase = get_supabase()
    supabase.table("tables").update({"status": status}).eq("id", table_id).execute()
