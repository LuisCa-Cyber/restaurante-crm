# database/storage.py — Subida de imágenes a Supabase Storage

import uuid
from database.supabase_client import get_supabase

BUCKET = "menu-images"


def subir_imagen(archivo_bytes: bytes, extension: str) -> str:
    """
    Sube una imagen al bucket de Supabase Storage.
    Retorna la URL pública de la imagen.
    """
    supabase = get_supabase()

    # Nombre único para evitar colisiones
    nombre_archivo = f"{uuid.uuid4()}.{extension}"

    supabase.storage.from_(BUCKET).upload(
        path=nombre_archivo,
        file=archivo_bytes,
        file_options={"content-type": f"image/{extension}"},
    )

    url = supabase.storage.from_(BUCKET).get_public_url(nombre_archivo)
    return url


def eliminar_imagen(url: str):
    """Elimina una imagen del bucket dado su URL pública."""
    supabase = get_supabase()
    # Extrae el nombre del archivo de la URL
    nombre_archivo = url.split(f"/{BUCKET}/")[-1]
    supabase.storage.from_(BUCKET).remove([nombre_archivo])
