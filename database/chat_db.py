# database/chat_db.py — Historial de conversaciones con IA

import json
from database.supabase_client import get_supabase


def guardar_sesion(restaurant_id: str, titulo: str, mensajes: list) -> dict:
    supabase = get_supabase()
    return (
        supabase.table("chat_sessions")
        .insert({
            "restaurant_id": restaurant_id,
            "titulo": titulo,
            "mensajes": json.dumps(mensajes, ensure_ascii=False),
        })
        .execute()
        .data[0]
    )


def obtener_sesiones(restaurant_id: str, limit: int = 30) -> list:
    supabase = get_supabase()
    return (
        supabase.table("chat_sessions")
        .select("id, titulo, created_at, mensajes")
        .eq("restaurant_id", restaurant_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )


def eliminar_sesion(sesion_id: str):
    supabase = get_supabase()
    supabase.table("chat_sessions").delete().eq("id", sesion_id).execute()
