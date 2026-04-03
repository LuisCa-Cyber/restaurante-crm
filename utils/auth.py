# utils/auth.py — Verificación de contraseñas para el panel admin

import bcrypt
from database.supabase_client import get_supabase


def verificar_password_admin(password_ingresada: str, restaurant_id: str) -> bool:
    """
    Consulta el usuario admin del restaurante en Supabase y verifica
    la contraseña con bcrypt.
    """
    supabase = get_supabase()
    respuesta = (
        supabase.table("users")
        .select("password_hash")
        .eq("restaurant_id", restaurant_id)
        .eq("role", "admin")
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        return False

    password_hash = respuesta.data[0]["password_hash"].encode("utf-8")
    return bcrypt.checkpw(password_ingresada.encode("utf-8"), password_hash)
