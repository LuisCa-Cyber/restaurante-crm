# pages/mesero.py — Vista del mesero: tomar pedidos y gestionar sus mesas

import streamlit as st
from datetime import datetime, timezone
from database.waiters_db import obtener_meseros
from database.tables_db import obtener_mesas, actualizar_estado_mesa
from database.menu import obtener_platos_disponibles
from database.orders import (
    crear_orden, obtener_orden_abierta_de_mesa,
    obtener_items_orden, agregar_items, marcar_item_entregado, cancelar_orden
)

# Categorías donde aplica la opción de sopa
CATEGORIAS_CON_SOPA = {"Plato del día", "Parrilla"}
PRECIO_SOPA = 2000

# Orden y filtro de categorías visibles en el menú
CATEGORIAS_MENU = ["Sopas", "Plato del día", "Parrilla", "Adiciones", "Postres", "Otros"]


def mostrar_vista_mesero(restaurante: dict):
    if not st.session_state.get("mesero_activo"):
        _seleccionar_mesero(restaurante)
        return

    mesero = st.session_state["mesero_activo"]

    col_titulo, col_salir = st.columns([4, 1])
    with col_titulo:
        st.title(f"👋 Hola, {mesero['name']}")
    with col_salir:
        if st.button("Salir", use_container_width=True):
            st.session_state.update({
                "modo": None, "mesero_activo": None,
                "vista_mesero": "mesas", "mesa_activa": None,
            })
            st.rerun()

    tab1, tab2 = st.tabs(["🪑 Mesas", "📋 Mis pendientes"])
    with tab1:
        _vista_mesas(restaurante, mesero)
    with tab2:
        _vista_pendientes(restaurante, mesero)


# ── Selección de mesero ────────────────────────────────────────────────────────

def _seleccionar_mesero(restaurante: dict):
    st.button("← Volver", on_click=lambda: st.session_state.update({"modo": None}))
    st.title("¿Quién eres?")

    meseros = obtener_meseros(restaurante["id"])
    if not meseros:
        st.warning("No hay meseros registrados. Pídele al admin que los configure.")
        return

    cols = st.columns(3)
    for i, mesero in enumerate(meseros):
        with cols[i % 3]:
            if st.button(f"👤 {mesero['name']}", key=f"sel_{mesero['id']}",
                         use_container_width=True, type="primary"):
                st.session_state["mesero_activo"] = mesero
                st.session_state["vista_mesero"] = "mesas"
                st.rerun()


# ── Vista de mesas ─────────────────────────────────────────────────────────────

def _vista_mesas(restaurante: dict, mesero: dict):
    st.markdown("### Mesas del restaurante")
    st.caption("Verde = disponible · Rojo = ocupada")

    mesas = obtener_mesas(restaurante["id"])
    if not mesas:
        st.info("No hay mesas configuradas. El admin debe crearlas en Configuración.")
        return

    cols = st.columns(4)
    for i, mesa in enumerate(mesas):
        with cols[i % 4]:
            orden = obtener_orden_abierta_de_mesa(mesa["id"])
            ocupada = mesa["status"] == "occupied"

            with st.container(border=True):
                st.markdown(f"### {mesa['name']}")
                if ocupada and orden:
                    st.markdown("🔴 Ocupada")
                    st.caption(f"Mesero: {orden['waiter_name']}")
                    items = obtener_items_orden(orden["id"])
                    st.caption(f"{len(items)} item(s)")

                    if st.button("Ver / Agregar", key=f"ver_{mesa['id']}",
                                 use_container_width=True):
                        st.session_state["mesa_activa"] = mesa
                        st.session_state["orden_activa_id"] = orden["id"]
                        st.session_state["vista_mesero"] = "orden"
                        st.rerun()

                    # Solo el mesero que atiende la mesa puede liberarla
                    if orden["waiter_id"] == mesero["id"]:
                        if st.button("🚫 Liberar mesa", key=f"liberar_{mesa['id']}",
                                     use_container_width=True):
                            cancelar_orden(orden["id"], mesa["id"])
                            st.rerun()
                else:
                    st.markdown("🟢 Disponible")
                    if st.button("Atender", key=f"atender_{mesa['id']}",
                                 use_container_width=True, type="primary"):
                        nueva_orden = crear_orden(
                            restaurante["id"], mesa["id"], mesa["name"],
                            mesero["id"], mesero["name"]
                        )
                        actualizar_estado_mesa(mesa["id"], "occupied")
                        st.session_state["mesa_activa"] = mesa
                        st.session_state["orden_activa_id"] = nueva_orden["id"]
                        st.session_state["vista_mesero"] = "orden"
                        st.rerun()

    if st.session_state.get("vista_mesero") == "orden":
        st.divider()
        _vista_orden(restaurante, mesero)


# ── Tomar / agregar items a la orden ──────────────────────────────────────────

def _vista_orden(restaurante: dict, mesero: dict):
    mesa = st.session_state.get("mesa_activa")
    order_id = st.session_state.get("orden_activa_id")

    if not mesa or not order_id:
        return

    st.markdown(f"## Orden — {mesa['name']}")

    # Items ya registrados
    items_actuales = obtener_items_orden(order_id)
    if items_actuales:
        st.markdown("**Pedido actual:**")
        for item in items_actuales:
            nota = f" _(nota: {item['notes']})_" if item.get("notes") else ""
            st.markdown(f"- {item['quantity']}x **{item['menu_item_name']}**{nota}")
        st.divider()

    # Agregar nuevos items
    st.markdown("**Agregar al pedido:**")
    platos = obtener_platos_disponibles(restaurante["id"])

    if not platos:
        st.warning("No hay platos disponibles en el menú.")
    else:
        carrito: dict[str, dict] = {}

        categorias: dict[str, list] = {}
        for p in platos:
            cat = p.get("category") or "Otros"
            if cat not in CATEGORIAS_MENU:
                cat = "Otros"
            categorias.setdefault(cat, []).append(p)

        for categoria in [c for c in CATEGORIAS_MENU if c in categorias]:
            items = categorias[categoria]
            with st.expander(categoria):
                for plato in items:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{plato['name']}**")
                        if plato.get("description"):
                            st.caption(plato["description"])
                    with col2:
                        precio_base = float(plato["price"])
                        st.markdown(f"💲{precio_base:,.0f}")
                    with col3:
                        cantidad = st.number_input(
                            "Cant.", min_value=0, max_value=20, value=0,
                            key=f"cant_{order_id}_{plato['id']}",
                            label_visibility="collapsed"
                        )

                    if cantidad > 0:
                        precio_final = precio_base
                        nombre_final = plato["name"]

                        # Opción de sopa para categorías aplicables
                        if categoria in CATEGORIAS_CON_SOPA:
                            con_sopa = st.checkbox(
                                f"Con sopa (+💲{PRECIO_SOPA:,.0f})",
                                key=f"sopa_{order_id}_{plato['id']}"
                            )
                            if con_sopa:
                                precio_final = precio_base + PRECIO_SOPA
                                nombre_final = f"{plato['name']} (con sopa)"

                        nota = st.text_input(
                            "Nota (opcional)",
                            placeholder="Ej: sin ensalada, extra papa...",
                            key=f"nota_{order_id}_{plato['id']}",
                        )
                        carrito[plato["id"]] = {
                            "menu_item_id": plato["id"],
                            "menu_item_name": nombre_final,
                            "unit_price": precio_final,
                            "quantity": cantidad,
                            "notes": nota.strip() if nota else None,
                        }

        col_enviar, col_cancelar = st.columns(2)
        with col_enviar:
            if st.button("✅ Enviar pedido", type="primary", use_container_width=True,
                         disabled=len(carrito) == 0):
                agregar_items(order_id, list(carrito.values()))
                st.session_state["vista_mesero"] = "mesas"
                st.session_state["mesa_activa"] = None
                st.session_state["orden_activa_id"] = None
                st.success("Pedido enviado.")
                st.rerun()
        with col_cancelar:
            if st.button("Cancelar", use_container_width=True):
                st.session_state["vista_mesero"] = "mesas"
                st.session_state["mesa_activa"] = None
                st.session_state["orden_activa_id"] = None
                st.rerun()


# ── Checklist de pendientes del mesero ────────────────────────────────────────

def _vista_pendientes(restaurante: dict, mesero: dict):
    st.markdown("### Lo que debes llevar")
    st.caption("🟢 < 5 min · 🟡 5-10 min · 🔴 > 10 min · Se actualiza cada 60 segundos")
    _pendientes_mesero_fragment(restaurante["id"], mesero["id"])


@st.fragment(run_every=60)
def _pendientes_mesero_fragment(restaurant_id: str, waiter_id: str):
    mesas = obtener_mesas(restaurant_id)
    hay_pendientes = False
    ahora = datetime.now(timezone.utc)

    for mesa in mesas:
        if mesa["status"] != "occupied":
            continue
        orden = obtener_orden_abierta_de_mesa(mesa["id"])
        if not orden or orden["waiter_id"] != waiter_id:
            continue

        items = obtener_items_orden(orden["id"])
        pendientes = [i for i in items if not i.get("delivered")]
        if not pendientes:
            continue

        hay_pendientes = True
        st.markdown(f"**{mesa['name']}**")
        for item in pendientes:
            creado = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            minutos = int((ahora - creado).total_seconds() / 60)
            alerta = "🔴" if minutos >= 10 else "🟡" if minutos >= 5 else "🟢"

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                nota = f" _(nota: {item['notes']})_" if item.get("notes") else ""
                st.markdown(f"{item['quantity']}x **{item['menu_item_name']}**{nota}")
            with col2:
                st.markdown(f"{alerta} {minutos} min")
            with col3:
                if st.button("✓", key=f"entregado_{item['id']}",
                             use_container_width=True):
                    marcar_item_entregado(item["id"], True)
                    st.rerun()
        st.divider()

    if not hay_pendientes:
        st.success("Todo entregado. ¡Sin pendientes!")
