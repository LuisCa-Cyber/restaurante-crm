# app.py — Punto de entrada principal de la aplicación

import streamlit as st
from config.settings import configurar_pagina
from views.home import mostrar_home
from views.mesero import mostrar_vista_mesero
from views.admin import mostrar_vista_admin
from database.supabase_client import get_supabase

configurar_pagina()

# Carga automática del restaurante (producto mono-restaurante)
if not st.session_state.get("restaurante_seleccionado"):
    supabase = get_supabase()
    datos = supabase.table("restaurants").select("*").eq("active", True).limit(1).execute().data
    if datos:
        st.session_state["restaurante_seleccionado"] = datos[0]

modo = st.session_state.get("modo")
restaurante = st.session_state.get("restaurante_seleccionado")

if modo == "mesero" and restaurante:
    mostrar_vista_mesero(restaurante)
elif modo == "admin" and restaurante:
    mostrar_vista_admin(restaurante)
else:
    mostrar_home()
