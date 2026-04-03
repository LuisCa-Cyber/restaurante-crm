# pages/home.py — Página inicial: tarjetas de restaurantes

import streamlit as st
from database.supabase_client import get_supabase


def obtener_restaurantes():
    supabase = get_supabase()
    return supabase.table("restaurants").select("*").eq("active", True).execute().data


def mostrar_home():
    st.title("🍽️ RestauranteCRM")
    st.markdown("Selecciona un restaurante para continuar.")
    st.divider()

    restaurantes = obtener_restaurantes()

    if not restaurantes:
        st.info("No hay restaurantes disponibles por ahora.")
        return

    cols = st.columns(3)
    for i, restaurante in enumerate(restaurantes):
        with cols[i % 3]:
            _mostrar_tarjeta(restaurante)


def _mostrar_tarjeta(restaurante: dict):
    with st.container(border=True):
        if restaurante.get("logo_url"):
            st.image(restaurante["logo_url"], width=80)
        else:
            st.markdown("### 🍴")

        st.subheader(restaurante["name"])
        if restaurante.get("address"):
            st.caption(restaurante["address"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Soy Mesero", key=f"mesero_{restaurante['id']}",
                         use_container_width=True, type="primary"):
                st.session_state["restaurante_seleccionado"] = restaurante
                st.session_state["modo"] = "mesero"
                st.rerun()
        with col2:
            if st.button("⚙️ Soy Admin", key=f"admin_{restaurante['id']}",
                         use_container_width=True, type="secondary"):
                st.session_state["restaurante_seleccionado"] = restaurante
                st.session_state["modo"] = "admin"
                st.rerun()
