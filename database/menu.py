# database/menu.py — Operaciones CRUD para platos del menú

from database.supabase_client import get_supabase


def obtener_todos_los_platos(restaurant_id: str) -> list:
    """Retorna todos los platos del restaurante (disponibles o no)."""
    supabase = get_supabase()
    return (
        supabase.table("menu_items")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .order("category")
        .execute()
        .data
    )


def obtener_platos_disponibles(restaurant_id: str) -> list:
    """Retorna solo los platos marcados como disponibles (vista cliente)."""
    supabase = get_supabase()
    return (
        supabase.table("menu_items")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .eq("available", True)
        .order("is_daily_special", desc=True)
        .execute()
        .data
    )


def obtener_platos_del_dia(restaurant_id: str) -> list:
    """Retorna solo los platos activados como plato del día (vista mesero)."""
    supabase = get_supabase()
    return (
        supabase.table("menu_items")
        .select("*")
        .eq("restaurant_id", restaurant_id)
        .eq("available", True)
        .eq("is_daily_special", True)
        .order("category")
        .execute()
        .data
    )


def crear_plato(restaurant_id: str, nombre: str, descripcion: str,
                precio: float, categoria: str) -> dict:
    """Crea un nuevo plato. La imagen se puede agregar después."""
    supabase = get_supabase()
    return (
        supabase.table("menu_items")
        .insert({
            "restaurant_id": restaurant_id,
            "name": nombre,
            "description": descripcion,
            "price": precio,
            "category": categoria,
            "available": True,
            "is_daily_special": False,
        })
        .execute()
        .data[0]
    )


def actualizar_plato(plato_id: str, campos: dict) -> dict:
    """Actualiza uno o varios campos de un plato."""
    supabase = get_supabase()
    return (
        supabase.table("menu_items")
        .update(campos)
        .eq("id", plato_id)
        .execute()
        .data[0]
    )


def eliminar_plato(plato_id: str):
    """Elimina un plato permanentemente."""
    supabase = get_supabase()
    supabase.table("menu_items").delete().eq("id", plato_id).execute()


def toggle_disponible(plato_id: str, disponible: bool):
    """Activa o desactiva la visibilidad de un plato en el menú."""
    supabase = get_supabase()
    supabase.table("menu_items").update({"available": disponible}).eq("id", plato_id).execute()


def toggle_plato_del_dia(plato_id: str, es_del_dia: bool):
    """Marca o desmarca un plato como plato del día."""
    supabase = get_supabase()
    supabase.table("menu_items").update({"is_daily_special": es_del_dia}).eq("id", plato_id).execute()


def actualizar_imagen(plato_id: str, image_url: str):
    """Guarda la URL pública de la imagen de un plato."""
    supabase = get_supabase()
    supabase.table("menu_items").update({"image_url": image_url}).eq("id", plato_id).execute()
