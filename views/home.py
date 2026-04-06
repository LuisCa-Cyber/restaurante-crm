# pages/home.py — Pantalla de inicio: selección de rol

import streamlit as st


def mostrar_home():
    restaurante = st.session_state.get("restaurante_seleccionado")
    nombre = restaurante["name"] if restaurante else "Restaurante"

    st.title(f"🍽️ {nombre}")
    st.divider()

    col_iz, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        st.markdown("### ¿Cómo ingresas hoy?")
        st.markdown("")
        if st.button("👤  Soy Mesero", use_container_width=True, type="primary"):
            st.session_state["modo"] = "mesero"
            st.rerun()
        st.markdown("")
        if st.button("⚙️  Administrador", use_container_width=True):
            st.session_state["modo"] = "admin"
            st.rerun()
