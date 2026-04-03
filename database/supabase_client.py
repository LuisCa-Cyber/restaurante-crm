# database/supabase_client.py — Cliente único de Supabase (singleton)

import streamlit as st
from supabase import create_client, Client
from config.settings import get_env


@st.cache_resource
def get_supabase() -> Client:
    """
    Devuelve un cliente de Supabase reutilizable.
    @st.cache_resource lo crea una sola vez por sesión de servidor.
    """
    url = get_env("SUPABASE_URL")
    key = get_env("SUPABASE_ANON_KEY")
    return create_client(url, key)
