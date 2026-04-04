# pages/admin.py — Panel de administración completo

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime, timezone

from utils.auth import verificar_password_admin
from database.menu import (
    obtener_todos_los_platos, crear_plato, actualizar_plato,
    eliminar_plato, toggle_disponible, toggle_plato_del_dia, actualizar_imagen
)
from database.storage import subir_imagen, eliminar_imagen
from database.tables_db import obtener_mesas, crear_mesa, eliminar_mesa, actualizar_estado_mesa
from database.waiters_db import obtener_meseros, crear_mesero, eliminar_mesero
from database.orders import (
    obtener_ordenes_abiertas, obtener_items_orden,
    cerrar_orden, obtener_ventas, cancelar_orden,
    registrar_modificacion, obtener_modificaciones,
    obtener_items_de_ordenes,
)

CATEGORIAS = ["Sopas", "Plato del día", "Parrilla", "Adiciones", "Postres", "Otros"]

# Categorías que aparecen en el tab de plato del día
CATEGORIAS_PLATO_DIA = {"Sopas", "Plato del día", "Parrilla", "Adiciones", "Postres", "Otros"}


def mostrar_vista_admin(restaurante: dict):
    st.button("← Volver", on_click=_cerrar_sesion)
    st.title(f"⚙️ Admin — {restaurante['name']}")

    if not st.session_state.get("admin_autenticado"):
        _pedir_password(restaurante)
    else:
        _panel_admin(restaurante)


def _cerrar_sesion():
    st.session_state.update({"modo": None, "admin_autenticado": False,
                              "orden_cerrando_id": None})


def _pedir_password(restaurante: dict):
    with st.form("login_admin"):
        st.subheader("Acceso de administrador")
        password = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Entrar")
    if enviado:
        if verificar_password_admin(password, restaurante["id"]):
            st.session_state["admin_autenticado"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")


def _panel_admin(restaurante: dict):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Órdenes activas",
        "⏳ Pendientes",
        "⭐ Platos del día",
        "🍽️ Gestión de platos",
        "⚙️ Configuración",
        "📊 Dashboard",
    ])
    with tab1:
        _tab_ordenes(restaurante)
    with tab2:
        _tab_pendientes(restaurante)
    with tab3:
        _tab_plato_del_dia(restaurante)
    with tab4:
        _tab_gestion_platos(restaurante)
    with tab5:
        _tab_configuracion(restaurante)
    with tab6:
        _tab_dashboard(restaurante)


# ── Tab 1: Órdenes activas ────────────────────────────────────────────────────

def _tab_ordenes(restaurante: dict):
    st.markdown("### Órdenes activas")

    if st.session_state.get("orden_cerrando_id"):
        _pantalla_cierre(restaurante)
        return

    _ordenes_fragment(restaurante["id"])


@st.fragment(run_every=5)
def _ordenes_fragment(restaurant_id: str):
    ordenes = obtener_ordenes_abiertas(restaurant_id)
    ahora = datetime.now(timezone.utc)

    if not ordenes:
        st.info("No hay órdenes activas en este momento.")
        return

    for orden in ordenes:
        items = obtener_items_orden(orden["id"])
        total = sum(i["unit_price"] * i["quantity"] for i in items)
        creado = datetime.fromisoformat(orden["created_at"].replace("Z", "+00:00"))
        minutos = int((ahora - creado).total_seconds() / 60)

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.markdown(f"### 🪑 {orden['table_name']}")
                st.caption(f"Mesero: {orden['waiter_name']}")
            with col2:
                st.markdown(f"**Total: 💲{total:,.0f}**")
                st.caption(f"{len(items)} item(s) · {minutos} min abierta")
            with col3:
                if st.button("Cerrar cuenta", key=f"cerrar_{orden['id']}",
                             type="primary", use_container_width=True):
                    st.session_state["orden_cerrando_id"] = orden["id"]
                    st.rerun()
            with col4:
                if st.button("🚫 Liberar", key=f"liberar_admin_{orden['id']}",
                             use_container_width=True):
                    cancelar_orden(orden["id"], orden["table_id"])
                    st.rerun()

            with st.expander("Ver detalle"):
                for item in items:
                    entregado = "✅" if item.get("delivered") else "⏳"
                    nota = f" _(nota: {item['notes']})_" if item.get("notes") else ""
                    st.markdown(
                        f"{entregado} {item['quantity']}x **{item['menu_item_name']}**{nota} "
                        f"— 💲{item['unit_price'] * item['quantity']:,.0f}"
                    )


def _pantalla_cierre(restaurante: dict):
    """Pantalla de confirmación antes de cerrar la cuenta, con opción de modificar."""
    order_id = st.session_state["orden_cerrando_id"]
    ordenes = obtener_ordenes_abiertas(restaurante["id"])
    orden = next((o for o in ordenes if o["id"] == order_id), None)

    if not orden:
        st.session_state["orden_cerrando_id"] = None
        st.rerun()
        return

    items = obtener_items_orden(order_id)
    total = sum(i["unit_price"] * i["quantity"] for i in items)

    # Recuperar total modificado si existe en session_state
    total_final = st.session_state.get(f"total_modificado_{order_id}", total)

    st.markdown("---")
    st.markdown(f"## 🧾 Cuenta — {orden['table_name']}")
    st.caption(f"Atendida por: {orden['waiter_name']}")
    st.markdown("---")

    for item in items:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            nota = f" _(nota: {item['notes']})_" if item.get("notes") else ""
            st.markdown(f"{item['menu_item_name']}{nota}")
        with col2:
            st.markdown(f"x{item['quantity']}")
        with col3:
            st.markdown(f"💲{item['unit_price'] * item['quantity']:,.0f}")

    # Modificaciones previas
    modificaciones = obtener_modificaciones(order_id)
    if modificaciones:
        st.markdown("**Modificaciones registradas:**")
        for m in modificaciones:
            st.caption(f"• {m['description']} (💲{m['original_total']:,.0f} → 💲{m['new_total']:,.0f})")

    st.markdown("---")
    st.markdown(f"## TOTAL A PAGAR: 💲{total_final:,.0f}")
    st.markdown("---")

    # Sección de modificación
    with st.expander("✏️ Modificar total"):
        with st.form("form_modificacion"):
            nuevo_total = st.number_input("Nuevo total", value=float(total_final),
                                          min_value=0.0, step=1000.0)
            motivo = st.text_input("Motivo de la modificación *",
                                   placeholder="Ej: descuento por error en pedido...")
            aplicar = st.form_submit_button("Aplicar modificación")

        if aplicar:
            if not motivo.strip():
                st.error("Debes escribir el motivo de la modificación.")
            else:
                registrar_modificacion(order_id, motivo.strip(), total_final, nuevo_total)
                st.session_state[f"total_modificado_{order_id}"] = nuevo_total
                st.success(f"Total modificado a 💲{nuevo_total:,.0f}. Motivo registrado.")
                st.rerun()

    col_confirmar, col_cancelar = st.columns(2)
    with col_confirmar:
        if st.button("✅ Confirmar pago y cerrar", type="primary",
                     use_container_width=True):
            cerrar_orden(order_id)
            actualizar_estado_mesa(orden["table_id"], "available")
            st.session_state["orden_cerrando_id"] = None
            st.session_state.pop(f"total_modificado_{order_id}", None)
            st.success(f"Cuenta cerrada. Total registrado: 💲{total_final:,.0f}")
            st.rerun()
    with col_cancelar:
        if st.button("← Volver a órdenes", use_container_width=True):
            st.session_state["orden_cerrando_id"] = None
            st.rerun()


# ── Tab 2: Pendientes ─────────────────────────────────────────────────────────

def _tab_pendientes(restaurante: dict):
    st.markdown("### ⏳ Items pendientes de entrega")
    st.caption("🟢 < 5 min · 🟡 5-10 min · 🔴 > 10 min · Se actualiza cada 5 segundos")
    _pendientes_fragment(restaurante["id"])


@st.fragment(run_every=5)
def _pendientes_fragment(restaurant_id: str):
    ordenes = obtener_ordenes_abiertas(restaurant_id)
    hay_pendientes = False
    ahora = datetime.now(timezone.utc)

    for orden in ordenes:
        items = obtener_items_orden(orden["id"])
        pendientes = [i for i in items if not i.get("delivered")]
        if not pendientes:
            continue

        hay_pendientes = True
        with st.container(border=True):
            st.markdown(f"**🪑 {orden['table_name']}** — Mesero: {orden['waiter_name']}")
            for item in pendientes:
                creado = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                minutos = int((ahora - creado).total_seconds() / 60)
                alerta = "🔴" if minutos >= 10 else "🟡" if minutos >= 5 else "🟢"

                col1, col2 = st.columns([5, 1])
                with col1:
                    nota = f" _(nota: {item['notes']})_" if item.get("notes") else ""
                    st.markdown(f"• {item['quantity']}x **{item['menu_item_name']}**{nota}")
                with col2:
                    st.markdown(f"{alerta} {minutos} min")

    if not hay_pendientes:
        st.success("✅ Todo entregado. No hay pendientes.")


# ── Tab 3: Plato del día ──────────────────────────────────────────────────────

def _tab_plato_del_dia(restaurante: dict):
    st.markdown("### Selecciona los platos del día")
    st.caption("Los activados aparecen primero. Se agrupan por sección.")

    platos = obtener_todos_los_platos(restaurante["id"])
    if not platos:
        st.info("No hay platos creados aún.")
        return

    # Agrupar por categoría — solo las secciones definidas
    categorias: dict[str, list] = {}
    for p in platos:
        cat = p.get("category") or "Otros"
        if cat not in CATEGORIAS_PLATO_DIA:
            cat = "Otros"
        categorias.setdefault(cat, []).append(p)

    orden = [c for c in CATEGORIAS if c in categorias]
    for categoria in orden:
        # Habilitados primero, luego el resto
        ordenados = sorted(categorias[categoria], key=lambda x: not x.get("is_daily_special", False))
        st.markdown(f"#### {categoria}")
        for plato in ordenados:
            es_del_dia = plato.get("is_daily_special", False)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                prefijo = "⭐ " if es_del_dia else ""
                st.markdown(f"{prefijo}**{plato['name']}**")
            with col2:
                st.markdown(f"💲{plato['price']:,.0f}")
            with col3:
                nuevo = st.toggle("Activo", value=es_del_dia,
                                  key=f"daily_{plato['id']}", label_visibility="collapsed")
                if nuevo != es_del_dia:
                    toggle_plato_del_dia(plato["id"], nuevo)
                    st.rerun()
        st.divider()


# ── Tab 4: Gestión de platos ──────────────────────────────────────────────────

def _tab_gestion_platos(restaurante: dict):
    st.markdown("### Platos del menú")

    if st.button("➕ Nuevo plato", type="primary"):
        st.session_state["mostrar_form_plato"] = True

    if st.session_state.get("mostrar_form_plato"):
        _form_crear_plato(restaurante)

    st.divider()
    _lista_platos(restaurante)


def _form_crear_plato(restaurante: dict):
    with st.form("form_crear_plato"):
        st.subheader("Nuevo plato")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre *")
            categoria = st.selectbox("Categoría", options=CATEGORIAS)
        with col2:
            precio = st.number_input("Precio *", min_value=0.0, step=500.0)
            disponible = st.checkbox("Disponible en menú", value=True)
        descripcion = st.text_area("Descripción")

        col_g, col_c = st.columns(2)
        with col_g:
            guardar = st.form_submit_button("Guardar", type="primary", use_container_width=True)
        with col_c:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)

    if guardar:
        if not nombre or precio <= 0:
            st.error("El nombre y el precio son obligatorios.")
        else:
            plato = crear_plato(restaurante["id"], nombre, descripcion, precio, categoria)
            if not disponible:
                toggle_disponible(plato["id"], False)
            st.session_state["mostrar_form_plato"] = False
            st.success(f"Plato '{nombre}' creado.")
            st.rerun()

    if cancelar:
        st.session_state["mostrar_form_plato"] = False
        st.rerun()


def _lista_platos(restaurante: dict):
    platos = obtener_todos_los_platos(restaurante["id"])
    if not platos:
        st.info("No hay platos creados aún.")
        return

    # Agrupar por categoría respetando el orden de CATEGORIAS
    por_categoria: dict[str, list] = {}
    for p in platos:
        cat = p.get("category") or "Otros"
        por_categoria.setdefault(cat, []).append(p)

    orden_cats = [c for c in CATEGORIAS if c in por_categoria]
    extras = [c for c in por_categoria if c not in CATEGORIAS]

    for cat in orden_cats + extras:
        st.markdown(f"#### {cat}")
        for plato in por_categoria[cat]:
            with st.expander(f"{'✅' if plato['available'] else '❌'} {plato['name']} — 💲{plato['price']:,.0f}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.form(f"edit_{plato['id']}"):
                        nombre = st.text_input("Nombre", value=plato["name"])
                        descripcion = st.text_area("Descripción", value=plato.get("description") or "")
                        col_p, col_c = st.columns(2)
                        with col_p:
                            precio = st.number_input("Precio", value=float(plato["price"]),
                                                     min_value=0.0, step=500.0)
                        with col_c:
                            cat_actual = plato.get("category") or "Otros"
                            idx = CATEGORIAS.index(cat_actual) if cat_actual in CATEGORIAS else len(CATEGORIAS) - 1
                            categoria = st.selectbox("Categoría", options=CATEGORIAS, index=idx)
                        disponible = st.checkbox("Disponible", value=plato["available"])

                        col_g, col_e = st.columns(2)
                        with col_g:
                            guardar = st.form_submit_button("💾 Guardar", use_container_width=True)
                        with col_e:
                            eliminar = st.form_submit_button("🗑️ Eliminar", use_container_width=True)

                    if guardar:
                        actualizar_plato(plato["id"], {
                            "name": nombre, "description": descripcion,
                            "price": precio, "category": categoria, "available": disponible,
                        })
                        st.success("Guardado.")
                        st.rerun()

                    if eliminar:
                        if plato.get("image_url"):
                            eliminar_imagen(plato["image_url"])
                        eliminar_plato(plato["id"])
                        st.rerun()

                with col2:
                    st.markdown("**Imagen del plato**")
                    if plato.get("image_url"):
                        st.image(plato["image_url"], use_container_width=True)
                        if st.button("🗑️ Quitar imagen", key=f"del_img_{plato['id']}"):
                            eliminar_imagen(plato["image_url"])
                            actualizar_imagen(plato["id"], None)
                            st.rerun()
                    else:
                        st.caption("Sin imagen")

                    archivo = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png", "webp"],
                                               key=f"upload_{plato['id']}", label_visibility="collapsed")
                    if archivo:
                        extension = archivo.name.split(".")[-1].lower()
                        with st.spinner("Subiendo..."):
                            url = subir_imagen(archivo.read(), extension)
                            if plato.get("image_url"):
                                eliminar_imagen(plato["image_url"])
                            actualizar_imagen(plato["id"], url)
                        st.success("Imagen subida.")
                        st.rerun()


# ── Tab 4: Configuración ──────────────────────────────────────────────────────

def _tab_configuracion(restaurante: dict):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🪑 Mesas")
        mesas = obtener_mesas(restaurante["id"])

        with st.form("form_nueva_mesa"):
            nombre_mesa = st.text_input("Nombre de la mesa", placeholder="Ej: Mesa 1, Barra, Terraza...")
            if st.form_submit_button("Agregar mesa", use_container_width=True):
                if nombre_mesa.strip():
                    crear_mesa(restaurante["id"], nombre_mesa.strip())
                    st.rerun()
                else:
                    st.error("Escribe un nombre.")

        st.divider()
        for mesa in mesas:
            col_nombre, col_estado, col_del = st.columns([3, 2, 1])
            with col_nombre:
                st.markdown(f"**{mesa['name']}**")
            with col_estado:
                estado = "🟢 Libre" if mesa["status"] == "available" else "🔴 Ocupada"
                st.caption(estado)
            with col_del:
                if mesa["status"] == "available":
                    if st.button("🗑️", key=f"del_mesa_{mesa['id']}"):
                        eliminar_mesa(mesa["id"])
                        st.rerun()

    with col2:
        st.markdown("### 👤 Meseros")
        meseros = obtener_meseros(restaurante["id"])

        with st.form("form_nuevo_mesero"):
            nombre_mesero = st.text_input("Nombre del mesero")
            if st.form_submit_button("Agregar mesero", use_container_width=True):
                if nombre_mesero.strip():
                    crear_mesero(restaurante["id"], nombre_mesero.strip())
                    st.rerun()
                else:
                    st.error("Escribe un nombre.")

        st.divider()
        for mesero in meseros:
            col_nombre, col_del = st.columns([4, 1])
            with col_nombre:
                st.markdown(f"**{mesero['name']}**")
            with col_del:
                if st.button("🗑️", key=f"del_mesero_{mesero['id']}"):
                    eliminar_mesero(mesero["id"])
                    st.rerun()


# ── Tab 5: Dashboard ──────────────────────────────────────────────────────────

def _tab_dashboard(restaurante: dict):
    st.markdown("### 📊 Dashboard de ventas")

    col1, col2 = st.columns(2)
    with col1:
        fecha_desde = st.date_input("Desde", value=date.today() - timedelta(days=30))
    with col2:
        fecha_hasta = st.date_input("Hasta", value=date.today())

    ventas = obtener_ventas(
        restaurante["id"],
        fecha_desde.isoformat(),
        fecha_hasta.isoformat(),
    )

    if not ventas:
        st.info("No hay ventas registradas en ese período.")
        return

    df = pd.DataFrame(ventas)
    df["closed_at"] = pd.to_datetime(df["closed_at"], utc=True).dt.tz_convert("America/Bogota")
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert("America/Bogota")
    df["fecha"] = df["closed_at"].dt.date
    df["hora"] = df["created_at"].dt.hour
    df["total"] = df["total"].astype(float)
    df["minutos_en_mesa"] = (df["closed_at"] - df["created_at"]).dt.total_seconds() / 60

    # Cargar items de las órdenes (para top platos e items/cuenta)
    order_ids = df["id"].tolist()
    items_ventas = obtener_items_de_ordenes(order_ids)
    if items_ventas:
        df_items = pd.DataFrame(items_ventas)
        df_items["quantity"] = df_items["quantity"].astype(int)
        df_items["unit_price"] = df_items["unit_price"].astype(float)
        df_items["ingresos"] = df_items["quantity"] * df_items["unit_price"]
    else:
        df_items = pd.DataFrame()

    # ── KPIs generales ─────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total ventas", f"💲{df['total'].sum():,.0f}")
    with col2:
        st.metric("🧾 Cuentas cerradas", len(df))
    with col3:
        st.metric("📊 Promedio por cuenta", f"💲{df['total'].mean():,.0f}")
    with col4:
        st.metric("🏆 Ticket máximo", f"💲{df['total'].max():,.0f}")

    # ── Métricas de tiempo y operación ─────────────────────────────────────────
    st.divider()
    st.markdown("#### ⏱️ Métricas de tiempo y operación")

    mesa_activa = df.groupby("table_name").size().idxmax()
    hora_pico = df.groupby("hora").size().idxmax()
    mejor_mesero = df.groupby("waiter_name")["total"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏱️ Tiempo promedio en mesa",
                  f"{df['minutos_en_mesa'].mean():.0f} min")
    with col2:
        st.metric("⚡ Atención más rápida",
                  f"{df['minutos_en_mesa'].min():.0f} min")
    with col3:
        st.metric("🐢 Atención más lenta",
                  f"{df['minutos_en_mesa'].max():.0f} min")
    with col4:
        st.metric("🪑 Mesa más activa", mesa_activa)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🕐 Hora pico", f"{hora_pico:02d}:00 – {hora_pico:02d}:59")
    with col2:
        st.metric("🌟 Mesero top ventas", mejor_mesero)
    with col3:
        if not df_items.empty:
            items_por_cuenta = df_items["quantity"].sum() / len(df)
            st.metric("🍽️ Items promedio/cuenta", f"{items_por_cuenta:.1f}")

    # Distribución de tiempos en mesa
    fig_tiempo = px.histogram(
        df, x="minutos_en_mesa", nbins=20,
        title="Distribución de tiempo en mesa (minutos)",
        labels={"minutos_en_mesa": "Minutos"},
        color_discrete_sequence=["#4ECDC4"],
    )
    fig_tiempo.update_layout(showlegend=False)
    st.plotly_chart(fig_tiempo, use_container_width=True)

    # Órdenes por hora del día
    ordenes_hora = df.groupby("hora").size().reset_index(name="Órdenes")
    fig_hora = px.bar(ordenes_hora, x="hora", y="Órdenes",
                      title="Órdenes por hora del día",
                      labels={"hora": "Hora"},
                      color_discrete_sequence=["#FF6B35"])
    st.plotly_chart(fig_hora, use_container_width=True)

    # ── Top 10 platos ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 🏆 Top platos vendidos")

    if not df_items.empty:
        # Mapa de categorías via platos del restaurante
        platos_info = obtener_todos_los_platos(restaurante["id"])
        cat_map = {p["id"]: p.get("category", "Otros") for p in platos_info}
        df_items["categoria"] = df_items["menu_item_id"].map(cat_map).fillna("Otros")

        categorias_disponibles = ["Todas"] + sorted(df_items["categoria"].unique().tolist())
        cat_filtro = st.selectbox("Filtrar por categoría", options=categorias_disponibles,
                                  key="filtro_categoria_top")

        df_filtrado = df_items if cat_filtro == "Todas" else df_items[df_items["categoria"] == cat_filtro]

        ranking = (
            df_filtrado.groupby("menu_item_name")
            .agg(cantidad=("quantity", "sum"), ingresos=("ingresos", "sum"))
            .reset_index()
            .sort_values("cantidad", ascending=False)
            .head(10)
        )
        ranking.index = range(1, len(ranking) + 1)

        fig_top = px.bar(
            ranking.reset_index(), x="menu_item_name", y="cantidad",
            title=f"Top 10 platos — {cat_filtro}",
            color_discrete_sequence=["#6C5CE7"],
            text="cantidad",
            labels={"menu_item_name": "Plato", "cantidad": "Unidades vendidas"},
        )
        fig_top.update_traces(textposition="outside")
        fig_top.update_layout(xaxis_tickangle=-30, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)

        ranking_mostrar = ranking.copy()
        ranking_mostrar.columns = ["Plato", "Unidades vendidas", "Ingresos"]
        ranking_mostrar["Ingresos"] = ranking_mostrar["Ingresos"].apply(lambda x: f"💲{x:,.0f}")
        st.dataframe(ranking_mostrar, use_container_width=True)
    else:
        st.info("No hay detalle de items para el período seleccionado.")

    st.divider()

    # ── Ventas por día y mesero ────────────────────────────────────────────────
    ventas_dia = df.groupby("fecha")["total"].sum().reset_index()
    ventas_dia.columns = ["Fecha", "Total"]
    fig = px.bar(ventas_dia, x="Fecha", y="Total",
                 title="Ventas por día", color_discrete_sequence=["#FF6B35"])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    ventas_mesero = df.groupby("waiter_name")["total"].sum().reset_index()
    ventas_mesero.columns = ["Mesero", "Total"]
    fig2 = px.pie(ventas_mesero, names="Mesero", values="Total",
                  title="Ventas por mesero")
    st.plotly_chart(fig2, use_container_width=True)

    # ── Tabla detalle ──────────────────────────────────────────────────────────
    st.markdown("### Detalle de cuentas cerradas")
    df_mostrar = df[["closed_at", "table_name", "waiter_name", "total", "minutos_en_mesa"]].copy()
    df_mostrar.columns = ["Fecha/Hora", "Mesa", "Mesero", "Total", "Min. en mesa"]
    df_mostrar["Total"] = df_mostrar["Total"].apply(lambda x: f"💲{x:,.0f}")
    df_mostrar["Min. en mesa"] = df_mostrar["Min. en mesa"].apply(lambda x: f"{x:.0f} min")
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
