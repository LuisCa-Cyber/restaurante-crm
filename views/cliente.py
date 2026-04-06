# pages/cliente.py — Vista pública del cliente: plato del día + menú completo

import streamlit as st
from database.menu import obtener_platos_disponibles


def mostrar_vista_cliente(restaurante: dict):
    st.button("← Volver", on_click=lambda: st.session_state.update({"modo": None}))

    st.title(f"🍴 {restaurante['name']}")
    if restaurante.get("address"):
        st.caption(restaurante["address"])

    platos = obtener_platos_disponibles(restaurante["id"])

    if not platos:
        st.info("Este restaurante aún no tiene platos disponibles.")
        return

    platos_del_dia = [p for p in platos if p.get("is_daily_special")]
    otros_platos = [p for p in platos if not p.get("is_daily_special")]

    # ── Plato del día ──────────────────────────────────────────────
    if platos_del_dia:
        st.divider()
        st.markdown("## ⭐ Plato del día")
        for plato in platos_del_dia:
            _tarjeta_destacada(plato)

    # ── Resto del menú ─────────────────────────────────────────────
    if otros_platos:
        st.divider()
        st.markdown("## 🍽️ Menú")

        categorias: dict[str, list] = {}
        for plato in otros_platos:
            cat = plato.get("category") or "Sin categoría"
            categorias.setdefault(cat, []).append(plato)

        for categoria, items in categorias.items():
            st.subheader(categoria)
            cols = st.columns(3)
            for i, plato in enumerate(items):
                with cols[i % 3]:
                    _tarjeta_plato(plato)
            st.markdown("")


def _tarjeta_destacada(plato: dict):
    """Tarjeta grande para el plato del día con imagen al lado."""
    with st.container(border=True):
        if plato.get("image_url"):
            col_img, col_info = st.columns([1, 2])
            with col_img:
                st.image(plato["image_url"], use_container_width=True)
            with col_info:
                _info_plato(plato, titulo_grande=True)
        else:
            _info_plato(plato, titulo_grande=True)


def _tarjeta_plato(plato: dict):
    """Tarjeta compacta para platos del menú general."""
    with st.container(border=True):
        if plato.get("image_url"):
            st.image(plato["image_url"], use_container_width=True)
        st.markdown(f"**{plato['name']}**")
        if plato.get("description"):
            st.caption(plato["description"])
        st.markdown(f"**💲 {plato['price']:,.0f}**")


def _info_plato(plato: dict, titulo_grande: bool = False):
    """Renderiza nombre, descripción y precio de un plato."""
    if titulo_grande:
        st.markdown(f"### {plato['name']}")
    else:
        st.markdown(f"**{plato['name']}**")

    if plato.get("description"):
        st.write(plato["description"])

    st.markdown(f"**💲 {plato['price']:,.0f}**")
