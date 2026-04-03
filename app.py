# app.py — Punto de entrada principal de la aplicación

import streamlit as st
from config.settings import configurar_pagina
from pages.home import mostrar_home
from pages.mesero import mostrar_vista_mesero
from pages.admin import mostrar_vista_admin

configurar_pagina()

modo = st.session_state.get("modo")
restaurante = st.session_state.get("restaurante_seleccionado")

if modo == "mesero" and restaurante:
    mostrar_vista_mesero(restaurante)
elif modo == "admin" and restaurante:
    mostrar_vista_admin(restaurante)
else:
    mostrar_home()
