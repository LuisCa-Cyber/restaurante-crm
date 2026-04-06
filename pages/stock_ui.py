# pages/stock_ui.py — Módulo de Stock / Inventario

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from database.stock_db import (
    CATEGORIAS_INSUMOS, UNIDADES, TIPOS_MOVIMIENTO,
    obtener_ingredientes, obtener_ingredientes_bajo_minimo,
    crear_ingrediente, actualizar_ingrediente, eliminar_ingrediente,
    registrar_movimiento, obtener_movimientos, valor_total_inventario,
)

COL_TZ = timezone(timedelta(hours=-5))


def mostrar_stock(restaurante: dict):
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen",
        "🥩 Insumos",
        "📥 Registrar movimiento",
        "📋 Historial",
    ])
    with tab1:
        _tab_resumen(restaurante)
    with tab2:
        _tab_insumos(restaurante)
    with tab3:
        _tab_registrar(restaurante)
    with tab4:
        _tab_historial(restaurante)


# ── Tab 1: Resumen ─────────────────────────────────────────────────────────────

def _tab_resumen(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])

    if not ingredientes:
        st.info("Aún no has registrado insumos. Ve a la pestaña **Insumos** para empezar.")
        return

    sin_stock = [i for i in ingredientes if float(i["stock_current"]) == 0]
    bajo_minimo = [
        i for i in ingredientes
        if 0 < float(i["stock_current"]) <= float(i["stock_min"])
    ]
    ok = [
        i for i in ingredientes
        if float(i["stock_current"]) > float(i["stock_min"])
    ]
    valor = valor_total_inventario(restaurante["id"])

    # ── KPIs ──────────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total insumos", len(ingredientes))
    with col2:
        st.metric("💰 Valor inventario", f"💲{valor:,.0f}")
    with col3:
        st.metric("⚠️ Bajo mínimo", len(bajo_minimo),
                  delta=None if not bajo_minimo else f"-{len(bajo_minimo)}",
                  delta_color="inverse")
    with col4:
        st.metric("🚨 Sin stock", len(sin_stock),
                  delta=None if not sin_stock else f"-{len(sin_stock)}",
                  delta_color="inverse")

    st.divider()

    # ── Alertas ───────────────────────────────────────────────────────────────
    if sin_stock or bajo_minimo:
        st.markdown("### 🚨 Requieren atención inmediata")

        if sin_stock:
            st.markdown("**Sin stock:**")
            for i in sin_stock:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.error(
                        f"🔴 **{i['name']}** ({i['category']})  "
                        f"— Stock actual: **0 {i['unit']}** "
                        f"| Mínimo: {i['stock_min']} {i['unit']}"
                    )
                with col_b:
                    if st.button("Registrar entrada", key=f"quick_entrada_{i['id']}",
                                 use_container_width=True):
                        st.session_state["stock_quick_ingrediente"] = i["id"]
                        st.session_state["stock_quick_tipo"] = "entrada"
                        st.rerun()

        if bajo_minimo:
            st.markdown("**Por debajo del mínimo:**")
            for i in bajo_minimo:
                pct = (float(i["stock_current"]) / float(i["stock_min"]) * 100) if float(i["stock_min"]) > 0 else 0
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.warning(
                        f"🟡 **{i['name']}** ({i['category']})  "
                        f"— Stock actual: **{_fmt_stock(i['stock_current'])} {i['unit']}** "
                        f"| Mínimo: {_fmt_stock(i['stock_min'])} {i['unit']} "
                        f"| {pct:.0f}% del mínimo"
                    )
                    st.progress(min(pct / 100, 1.0))
                with col_b:
                    if st.button("Registrar entrada", key=f"quick_entrada_b_{i['id']}",
                                 use_container_width=True):
                        st.session_state["stock_quick_ingrediente"] = i["id"]
                        st.session_state["stock_quick_tipo"] = "entrada"
                        st.rerun()
    else:
        st.success("✅ Todo el inventario está por encima del mínimo. ¡Bien abastecido!")

    # ── Estado general ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📦 Estado general del inventario")

    categorias_presentes = sorted(set(i["category"] for i in ingredientes))
    cat_filtro = st.selectbox("Filtrar por categoría", ["Todas"] + categorias_presentes,
                              key="resumen_cat_filtro")

    lista = ingredientes if cat_filtro == "Todas" else [i for i in ingredientes if i["category"] == cat_filtro]

    for item in lista:
        stock = float(item["stock_current"])
        minimo = float(item["stock_min"])
        if stock == 0:
            icono = "🔴"
        elif stock <= minimo:
            icono = "🟡"
        else:
            icono = "🟢"

        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.markdown(f"{icono} **{item['name']}**")
            st.caption(item["category"])
        with col2:
            st.markdown(f"**{_fmt_stock(item['stock_current'])} {item['unit']}**")
            st.caption(f"Mín: {_fmt_stock(item['stock_min'])} {item['unit']}")
        with col3:
            st.markdown(f"💲{float(item['cost_per_unit']):,.0f}/{item['unit']}")
        with col4:
            valor_item = stock * float(item["cost_per_unit"])
            st.markdown(f"💰 {f'💲{valor_item:,.0f}'}")
        with col5:
            if minimo > 0:
                pct = min(stock / minimo, 2.0)
                st.progress(min(pct / 2, 1.0))


# ── Tab 2: Insumos ─────────────────────────────────────────────────────────────

def _tab_insumos(restaurante: dict):
    col_titulo, col_nuevo = st.columns([4, 1])
    with col_titulo:
        st.markdown("### Gestión de insumos")
    with col_nuevo:
        st.markdown("")
        if st.button("➕ Nuevo insumo", use_container_width=True, type="primary"):
            st.session_state["stock_form_nuevo"] = True

    if st.session_state.get("stock_form_nuevo"):
        _form_nuevo_insumo(restaurante)
        st.divider()

    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("No hay insumos registrados. Crea el primero con el botón de arriba.")
        return

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cats = ["Todas"] + sorted(set(i["category"] for i in ingredientes))
        cat_filtro = st.selectbox("Categoría", cats, key="insumos_cat")
    with col_f2:
        busqueda = st.text_input("Buscar insumo", placeholder="Escribe para filtrar...",
                                 key="insumos_busqueda")

    lista = ingredientes
    if cat_filtro != "Todas":
        lista = [i for i in lista if i["category"] == cat_filtro]
    if busqueda:
        lista = [i for i in lista if busqueda.lower() in i["name"].lower()]

    st.caption(f"{len(lista)} insumo(s) encontrado(s)")
    st.divider()

    for item in lista:
        stock = float(item["stock_current"])
        minimo = float(item["stock_min"])
        icono = "🔴" if stock == 0 else ("🟡" if stock <= minimo else "🟢")

        with st.expander(f"{icono} **{item['name']}** — {_fmt_stock(item['stock_current'])} {item['unit']} | 💲{float(item['cost_per_unit']):,.0f}/{item['unit']}"):
            with st.form(f"edit_insumo_{item['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre", value=item["name"])
                    unidad_idx = UNIDADES.index(item["unit"]) if item["unit"] in UNIDADES else 0
                    unidad = st.selectbox("Unidad", UNIDADES, index=unidad_idx)
                    cat_idx = CATEGORIAS_INSUMOS.index(item["category"]) if item["category"] in CATEGORIAS_INSUMOS else len(CATEGORIAS_INSUMOS) - 1
                    categoria = st.selectbox("Categoría", CATEGORIAS_INSUMOS, index=cat_idx)
                with col2:
                    stock_min = st.number_input("Stock mínimo", value=float(item["stock_min"]),
                                                min_value=0.0, step=0.5,
                                                help="Recibirás alerta cuando baje de este nivel")
                    costo = st.number_input("Costo por unidad (💲)", value=float(item["cost_per_unit"]),
                                            min_value=0.0, step=100.0)
                    st.metric("Stock actual", f"{_fmt_stock(item['stock_current'])} {item['unit']}")

                col_g, col_e = st.columns(2)
                with col_g:
                    guardar = st.form_submit_button("💾 Guardar cambios", use_container_width=True)
                with col_e:
                    eliminar = st.form_submit_button("🗑️ Eliminar insumo", use_container_width=True)

            if guardar:
                actualizar_ingrediente(item["id"], {
                    "name": nombre,
                    "unit": unidad,
                    "category": categoria,
                    "stock_min": stock_min,
                    "cost_per_unit": costo,
                })
                st.success("Guardado.")
                st.rerun()

            if eliminar:
                eliminar_ingrediente(item["id"])
                st.rerun()


def _form_nuevo_insumo(restaurante: dict):
    with st.form("form_nuevo_insumo"):
        st.markdown("#### Nuevo insumo")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre *", placeholder="Ej: Pechuga de pollo")
            categoria = st.selectbox("Categoría *", CATEGORIAS_INSUMOS)
        with col2:
            unidad = st.selectbox("Unidad de medida *", UNIDADES)
            stock_min = st.number_input("Stock mínimo de alerta", min_value=0.0,
                                        step=0.5, value=1.0,
                                        help="Se mostrará alerta cuando el stock baje de este valor")
            costo = st.number_input("Costo por unidad (💲)", min_value=0.0, step=100.0,
                                    help="Usado para calcular el valor del inventario")

        col_g, col_c = st.columns(2)
        with col_g:
            guardar = st.form_submit_button("Crear insumo", type="primary", use_container_width=True)
        with col_c:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)

    if guardar:
        if not nombre.strip():
            st.error("El nombre es obligatorio.")
        else:
            crear_ingrediente(restaurante["id"], nombre.strip(), unidad,
                              stock_min, costo, categoria)
            st.session_state["stock_form_nuevo"] = False
            st.success(f"✅ '{nombre}' creado con stock inicial 0 {unidad}. Registra una entrada para cargarlo.")
            st.rerun()

    if cancelar:
        st.session_state["stock_form_nuevo"] = False
        st.rerun()


# ── Tab 3: Registrar movimiento ────────────────────────────────────────────────

def _tab_registrar(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("Primero registra insumos en la pestaña **Insumos**.")
        return

    st.markdown("### Registrar movimiento de stock")

    # Si viene de un botón rápido desde Resumen, preseleccionar
    default_tipo = st.session_state.pop("stock_quick_tipo", "entrada")
    default_ing = st.session_state.pop("stock_quick_ingrediente", None)

    tipo_label = st.radio(
        "Tipo de movimiento",
        list(TIPOS_MOVIMIENTO.values()),
        horizontal=True,
        index=list(TIPOS_MOVIMIENTO.keys()).index(default_tipo),
        key="mov_tipo",
    )
    tipo = [k for k, v in TIPOS_MOVIMIENTO.items() if v == tipo_label][0]

    st.divider()

    # Selector de insumo
    nombres_ing = {i["id"]: f"{i['name']} ({_fmt_stock(i['stock_current'])} {i['unit']} disponibles)" for i in ingredientes}
    opciones_ids = list(nombres_ing.keys())
    default_idx = opciones_ids.index(default_ing) if default_ing and default_ing in opciones_ids else 0

    ing_id = st.selectbox(
        "Insumo",
        options=opciones_ids,
        format_func=lambda x: nombres_ing[x],
        index=default_idx,
        key="mov_ingrediente",
    )
    ing_seleccionado = next(i for i in ingredientes if i["id"] == ing_id)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Stock actual", f"{_fmt_stock(ing_seleccionado['stock_current'])} {ing_seleccionado['unit']}")
    with col2:
        st.metric("Stock mínimo", f"{_fmt_stock(ing_seleccionado['stock_min'])} {ing_seleccionado['unit']}")

    st.divider()

    with st.form("form_movimiento"):
        if tipo == "ajuste":
            st.caption("💡 Ingresa la cantidad **real** que contaste en la bodega.")
            cantidad = st.number_input(
                f"Nuevo stock total ({ing_seleccionado['unit']})",
                min_value=0.0, step=0.1, value=float(ing_seleccionado["stock_current"]),
            )
            motivo = st.text_input("Motivo del ajuste *",
                                   placeholder="Ej: Conteo físico del día, corrección de error...")
            costo = None

        elif tipo == "entrada":
            st.caption("💡 Registra una compra o recepción de mercancía.")
            cantidad = st.number_input(
                f"Cantidad recibida ({ing_seleccionado['unit']})",
                min_value=0.01, step=0.1,
            )
            col_m, col_c = st.columns(2)
            with col_m:
                motivo = st.text_input("Proveedor / motivo",
                                       placeholder="Ej: Compra a Frigorífico Andino")
            with col_c:
                costo = st.number_input(
                    "Precio de compra por unidad (💲)",
                    min_value=0.0, step=100.0,
                    value=float(ing_seleccionado["cost_per_unit"]),
                    help="Actualiza el costo del insumo si cambió",
                )

        elif tipo == "merma":
            st.caption("💡 Registra pérdida por vencimiento, daño o desperdicio.")
            cantidad = st.number_input(
                f"Cantidad a descontar ({ing_seleccionado['unit']})",
                min_value=0.01, step=0.1,
            )
            motivo = st.text_input("Causa de la merma *",
                                   placeholder="Ej: Producto vencido, caída accidental, plagas...")
            costo = None

        else:  # salida
            st.caption("💡 Registra una salida especial (consumo interno, donación, etc.).")
            cantidad = st.number_input(
                f"Cantidad a descontar ({ing_seleccionado['unit']})",
                min_value=0.01, step=0.1,
            )
            motivo = st.text_input("Motivo",
                                   placeholder="Ej: Consumo personal, donación...")
            costo = None

        enviado = st.form_submit_button("✅ Registrar", type="primary", use_container_width=True)

    if enviado:
        if tipo != "entrada" and not str(motivo).strip():
            st.error("El motivo es obligatorio.")
        else:
            resultado = registrar_movimiento(
                restaurante["id"], ing_id, tipo, cantidad,
                str(motivo).strip() if motivo else "",
                costo if tipo == "entrada" else None,
            )
            ing_actualizado = next(i for i in obtener_ingredientes(restaurante["id"]) if i["id"] == ing_id)
            nuevo_stock = float(ing_actualizado["stock_current"])

            if tipo == "entrada":
                st.success(f"✅ Entrada registrada. Stock actualizado a **{_fmt_stock(nuevo_stock)} {ing_seleccionado['unit']}**")
            elif tipo == "ajuste":
                delta = cantidad - float(ing_seleccionado["stock_current"])
                signo = "+" if delta >= 0 else ""
                st.success(f"✅ Ajuste registrado. Stock actualizado a **{_fmt_stock(nuevo_stock)} {ing_seleccionado['unit']}** ({signo}{_fmt_stock(delta)})")
            elif tipo == "merma":
                st.warning(f"⚠️ Merma registrada. Stock actualizado a **{_fmt_stock(nuevo_stock)} {ing_seleccionado['unit']}**")
            else:
                st.success(f"✅ Salida registrada. Stock actualizado a **{_fmt_stock(nuevo_stock)} {ing_seleccionado['unit']}**")

            st.rerun()


# ── Tab 4: Historial ───────────────────────────────────────────────────────────

def _tab_historial(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("Sin movimientos registrados aún.")
        return

    st.markdown("### Historial de movimientos")

    col1, col2 = st.columns(2)
    with col1:
        opciones_ing = {"Todos": None}
        opciones_ing.update({i["name"]: i["id"] for i in ingredientes})
        ing_filtro_nombre = st.selectbox("Insumo", list(opciones_ing.keys()), key="hist_ing")
        ing_filtro_id = opciones_ing[ing_filtro_nombre]
    with col2:
        tipo_filtro = st.selectbox("Tipo", ["Todos"] + list(TIPOS_MOVIMIENTO.values()), key="hist_tipo")

    movimientos = obtener_movimientos(restaurante["id"], ing_filtro_id, limit=200)

    if not movimientos:
        st.info("No hay movimientos con los filtros seleccionados.")
        return

    # Filtrar por tipo en Python
    if tipo_filtro != "Todos":
        tipo_key = [k for k, v in TIPOS_MOVIMIENTO.items() if v == tipo_filtro][0]
        movimientos = [m for m in movimientos if m["type"] == tipo_key]

    # Construir DataFrame
    filas = []
    for m in movimientos:
        fecha_utc = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
        fecha_col = fecha_utc.astimezone(COL_TZ)
        ing_data = m.get("ingredients") or {}
        nombre_ing = ing_data.get("name", "—")
        unidad = ing_data.get("unit", "")
        cantidad = float(m["quantity"])
        signo = "+" if cantidad >= 0 else ""

        filas.append({
            "Fecha/Hora": fecha_col.strftime("%d/%m/%Y %H:%M"),
            "Insumo": nombre_ing,
            "Tipo": TIPOS_MOVIMIENTO.get(m["type"], m["type"]),
            "Cantidad": f"{signo}{_fmt_stock(cantidad)} {unidad}",
            "Motivo": m.get("reason") or "—",
            "Costo/u": f"💲{float(m['cost_per_unit']):,.0f}" if m.get("cost_per_unit") else "—",
        })

    df = pd.DataFrame(filas)

    # Resumen rápido
    total_entradas = sum(float(m["quantity"]) for m in movimientos if m["type"] == "entrada")
    total_mermas = sum(abs(float(m["quantity"])) for m in movimientos if m["type"] == "merma")
    col_e, col_m, col_t = st.columns(3)
    with col_e:
        st.metric("📥 Total entradas", f"{_fmt_stock(total_entradas)}")
    with col_m:
        st.metric("🗑️ Total mermas", f"{_fmt_stock(total_mermas)}")
    with col_t:
        st.metric("📋 Movimientos mostrados", len(df))

    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt_stock(valor) -> str:
    """Formatea cantidades de stock: sin decimales si es entero, con 1 decimal si no."""
    v = float(valor)
    return f"{v:.0f}" if v == int(v) else f"{v:.2f}".rstrip("0")
