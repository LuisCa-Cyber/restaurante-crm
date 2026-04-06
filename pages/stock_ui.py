# pages/stock_ui.py — Módulo de Stock / Inventario

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from database.stock_db import (
    CATEGORIAS_INSUMOS, UNIDADES,
    obtener_ingredientes, crear_ingrediente, actualizar_ingrediente,
    eliminar_ingrediente, registrar_movimiento, obtener_movimientos,
    valor_total_inventario,
)

COL_TZ = timezone(timedelta(hours=-5))

# Acciones en lenguaje cotidiano
ACCIONES = {
    "llegó": {
        "tipo": "entrada",
        "titulo": "📥 Llegó mercancía",
        "desc": "Registra una compra o entrega de proveedor",
        "color": "primary",
    },
    "dañó": {
        "tipo": "merma",
        "titulo": "🗑️ Se dañó o venció",
        "desc": "Producto que hay que tirar (caducado, caída, daño)",
        "color": "secondary",
    },
    "conté": {
        "tipo": "ajuste",
        "titulo": "🔢 Hice un conteo",
        "desc": "Ajustar el stock al valor real que encontraste en bodega",
        "color": "secondary",
    },
}


def mostrar_stock(restaurante: dict):
    tab1, tab2, tab3 = st.tabs([
        "📦 Inventario",
        "🥩 Mis insumos",
        "📋 Historial",
    ])
    with tab1:
        _tab_inventario(restaurante)
    with tab2:
        _tab_insumos(restaurante)
    with tab3:
        _tab_historial(restaurante)


# ── Tab 1: Inventario (vista principal) ───────────────────────────────────────

def _tab_inventario(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])

    if not ingredientes:
        st.info("Aún no tienes insumos registrados.")
        st.markdown("Ve a la pestaña **🥩 Mis insumos** y crea los productos que manejas en tu cocina.")
        return

    # ── Acciones rápidas ──────────────────────────────────────────────────────
    accion_activa = st.session_state.get("stock_accion")

    if not accion_activa:
        st.markdown("### ¿Qué pasó hoy con el inventario?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Llegó mercancía", use_container_width=True, type="primary",
                         help="Registra una compra o entrega de proveedor"):
                st.session_state["stock_accion"] = "llegó"
                st.rerun()
        with col2:
            if st.button("🗑️ Se dañó o venció", use_container_width=True,
                         help="Producto que hay que tirar"):
                st.session_state["stock_accion"] = "dañó"
                st.rerun()
        with col3:
            if st.button("🔢 Hice un conteo", use_container_width=True,
                         help="Corrige el stock al número real que contaste"):
                st.session_state["stock_accion"] = "conté"
                st.rerun()
    else:
        _formulario_accion(restaurante, ingredientes, accion_activa)
        return

    st.divider()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    sin_stock  = [i for i in ingredientes if float(i["stock_current"]) == 0]
    bajo_min   = [i for i in ingredientes if 0 < float(i["stock_current"]) <= float(i["stock_min"])]
    valor      = valor_total_inventario(restaurante["id"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Insumos", len(ingredientes))
    with col2:
        st.metric("💰 Valor en bodega", f"💲{valor:,.0f}")
    with col3:
        st.metric("🟡 Bajo mínimo", len(bajo_min))
    with col4:
        st.metric("🔴 Sin stock", len(sin_stock))

    # ── Alertas ───────────────────────────────────────────────────────────────
    if sin_stock or bajo_min:
        st.divider()
        st.markdown("### ⚠️ Necesitan reposición")

        for i in sin_stock:
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.error(f"🔴 **{i['name']}** — Sin stock  |  Mínimo: {_fmt(i['stock_min'])} {i['unit']}")
            with col_b:
                if st.button("Comprar", key=f"alerta_comprar_{i['id']}", use_container_width=True):
                    st.session_state["stock_accion"] = "llegó"
                    st.session_state["stock_ing_presel"] = i["id"]
                    st.rerun()

        for i in bajo_min:
            pct = float(i["stock_current"]) / float(i["stock_min"]) * 100 if float(i["stock_min"]) > 0 else 0
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.warning(
                    f"🟡 **{i['name']}** — {_fmt(i['stock_current'])} {i['unit']} disponibles  "
                    f"|  Mínimo: {_fmt(i['stock_min'])} {i['unit']}  |  {pct:.0f}% del mínimo"
                )
                st.progress(min(pct / 100, 1.0))
            with col_b:
                if st.button("Comprar", key=f"alerta_bajo_{i['id']}", use_container_width=True):
                    st.session_state["stock_accion"] = "llegó"
                    st.session_state["stock_ing_presel"] = i["id"]
                    st.rerun()
    else:
        st.success("✅ Todo el inventario está sobre el mínimo.")

    # ── Tabla de estado ───────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Estado actual")

    cats = ["Todas"] + sorted(set(i["category"] for i in ingredientes))
    cat_sel = st.selectbox("Categoría", cats, key="inv_cat", label_visibility="collapsed")
    lista = ingredientes if cat_sel == "Todas" else [i for i in ingredientes if i["category"] == cat_sel]

    for item in lista:
        stock  = float(item["stock_current"])
        minimo = float(item["stock_min"])
        icono  = "🔴" if stock == 0 else ("🟡" if stock <= minimo else "🟢")
        valor_item = stock * float(item["cost_per_unit"])

        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        with col1:
            st.markdown(f"{icono} **{item['name']}**")
            st.caption(item["category"])
        with col2:
            st.markdown(f"**{_fmt(item['stock_current'])} {item['unit']}**")
            st.caption(f"Mín: {_fmt(item['stock_min'])} {item['unit']}")
        with col3:
            st.markdown(f"💲{float(item['cost_per_unit']):,.0f} / {item['unit']}")
        with col4:
            st.markdown(f"💰 💲{valor_item:,.0f}")
            if minimo > 0:
                st.progress(min(stock / minimo / 2, 1.0))
        with col5:
            if st.button("📥", key=f"inv_entrada_{item['id']}",
                         help="Registrar entrada para este insumo"):
                st.session_state["stock_accion"] = "llegó"
                st.session_state["stock_ing_presel"] = item["id"]
                st.rerun()


def _formulario_accion(restaurante: dict, ingredientes: list, accion: str):
    """Formulario inline para las 3 acciones principales."""
    cfg = ACCIONES[accion]

    col_titulo, col_cancelar = st.columns([4, 1])
    with col_titulo:
        st.markdown(f"## {cfg['titulo']}")
        st.caption(cfg["desc"])
    with col_cancelar:
        st.markdown("")
        if st.button("✕ Cancelar", use_container_width=True):
            st.session_state.pop("stock_accion", None)
            st.session_state.pop("stock_ing_presel", None)
            st.rerun()

    st.divider()

    # Selector de insumo con preselección
    presel = st.session_state.pop("stock_ing_presel", None)
    ids = [i["id"] for i in ingredientes]
    default_idx = ids.index(presel) if presel and presel in ids else 0

    ing_id = st.selectbox(
        "¿Cuál insumo?",
        options=ids,
        format_func=lambda x: next(
            f"{i['name']}  ({_fmt(i['stock_current'])} {i['unit']} en bodega)"
            for i in ingredientes if i["id"] == x
        ),
        index=default_idx,
    )
    ing = next(i for i in ingredientes if i["id"] == ing_id)

    # Indicador del estado actual
    stock_actual = float(ing["stock_current"])
    minimo = float(ing["stock_min"])
    icono = "🔴" if stock_actual == 0 else ("🟡" if stock_actual <= minimo else "🟢")
    st.info(f"{icono} **{ing['name']}** tiene actualmente **{_fmt(ing['stock_current'])} {ing['unit']}** en bodega.")

    st.divider()

    with st.form("form_accion_stock"):
        if accion == "llegó":
            st.markdown("**¿Cuánto llegó?**")
            col1, col2 = st.columns(2)
            with col1:
                cantidad = st.number_input(
                    f"Cantidad ({ing['unit']})",
                    min_value=0.01, step=0.5,
                    help="Escribe exactamente cuánto recibiste",
                )
            with col2:
                costo = st.number_input(
                    "Precio que pagaste por unidad (💲)",
                    min_value=0.0, step=100.0,
                    value=float(ing["cost_per_unit"]),
                    help="Si el precio cambió, actualízalo aquí",
                )
            motivo = st.text_input(
                "¿De dónde viene? (opcional)",
                placeholder="Ej: Frigorífico Andino, Mercado Central...",
            )
            enviado = st.form_submit_button(
                f"✅ Registrar — llegaron {'{cantidad}'} {ing['unit']}".replace("{cantidad}", "..."),
                type="primary", use_container_width=True,
            )

        elif accion == "dañó":
            st.markdown("**¿Cuánto hay que tirar?**")
            cantidad = st.number_input(
                f"Cantidad a descartar ({ing['unit']})",
                min_value=0.01, step=0.5,
                help=f"Tienes {_fmt(ing['stock_current'])} {ing['unit']} en bodega",
            )
            motivo = st.text_input(
                "¿Por qué se dañó? *",
                placeholder="Ej: Se venció, se cayó, olía mal, plagas...",
            )
            enviado = st.form_submit_button(
                "🗑️ Registrar descarte", type="primary", use_container_width=True,
            )
            costo = None

        else:  # conté
            st.markdown("**¿Cuánto contaste en bodega?**")
            st.caption(f"El sistema tiene registrado {_fmt(ing['stock_current'])} {ing['unit']}. "
                       "Si el número real es diferente, escríbelo aquí.")
            cantidad = st.number_input(
                f"Cantidad real contada ({ing['unit']})",
                min_value=0.0, step=0.5,
                value=float(ing["stock_current"]),
            )
            motivo = st.text_input(
                "¿Por qué hay diferencia? (opcional)",
                placeholder="Ej: Conteo físico de cierre del día, corrección de error...",
            )
            enviado = st.form_submit_button(
                "🔢 Ajustar inventario", type="primary", use_container_width=True,
            )
            costo = None

    if enviado:
        if accion == "dañó" and not motivo.strip():
            st.error("Escribe por qué se dañó el producto.")
            return

        registrar_movimiento(
            restaurante["id"], ing_id, cfg["tipo"], cantidad,
            motivo.strip() if motivo else "",
            costo if accion == "llegó" else None,
        )

        # Calcular nuevo stock para el mensaje
        ings_nuevo = obtener_ingredientes(restaurante["id"])
        ing_nuevo = next(i for i in ings_nuevo if i["id"] == ing_id)
        nuevo_stock = float(ing_nuevo["stock_current"])

        if accion == "llegó":
            st.success(
                f"✅ Registrado. **{ing['name']}** pasó de {_fmt(stock_actual)} a "
                f"**{_fmt(nuevo_stock)} {ing['unit']}** en bodega."
            )
        elif accion == "dañó":
            st.warning(
                f"🗑️ Registrado. **{ing['name']}** pasó de {_fmt(stock_actual)} a "
                f"**{_fmt(nuevo_stock)} {ing['unit']}** en bodega."
            )
        else:
            delta = nuevo_stock - stock_actual
            signo = "+" if delta >= 0 else ""
            st.success(
                f"🔢 Ajuste registrado. **{ing['name']}** queda en "
                f"**{_fmt(nuevo_stock)} {ing['unit']}** ({signo}{_fmt(delta)})."
            )

        st.session_state.pop("stock_accion", None)
        st.session_state.pop("stock_ing_presel", None)
        st.rerun()


# ── Tab 2: Mis insumos ─────────────────────────────────────────────────────────

def _tab_insumos(restaurante: dict):
    col_t, col_n = st.columns([4, 1])
    with col_t:
        st.markdown("### Mis insumos")
        st.caption("Aquí defines qué productos maneja tu cocina, su unidad y el mínimo de alerta.")
    with col_n:
        st.markdown("")
        if st.button("➕ Agregar", use_container_width=True, type="primary"):
            st.session_state["stock_form_nuevo"] = True

    if st.session_state.get("stock_form_nuevo"):
        _form_nuevo_insumo(restaurante)
        st.divider()

    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("No tienes insumos aún. Crea el primero con el botón de arriba.")
        return

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cats = ["Todas"] + sorted(set(i["category"] for i in ingredientes))
        cat_f = st.selectbox("Categoría", cats, key="ins_cat")
    with col_f2:
        busq = st.text_input("Buscar", placeholder="Nombre del insumo...", key="ins_busq")

    lista = ingredientes
    if cat_f != "Todas":
        lista = [i for i in lista if i["category"] == cat_f]
    if busq:
        lista = [i for i in lista if busq.lower() in i["name"].lower()]

    st.caption(f"{len(lista)} insumo(s)")
    st.divider()

    for item in lista:
        stock  = float(item["stock_current"])
        minimo = float(item["stock_min"])
        icono  = "🔴" if stock == 0 else ("🟡" if stock <= minimo else "🟢")

        with st.expander(
            f"{icono} **{item['name']}** — "
            f"{_fmt(item['stock_current'])} {item['unit']} en bodega  |  "
            f"Mín: {_fmt(item['stock_min'])} {item['unit']}  |  "
            f"💲{float(item['cost_per_unit']):,.0f}/{item['unit']}"
        ):
            with st.form(f"edit_{item['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre   = st.text_input("Nombre", value=item["name"])
                    u_idx    = UNIDADES.index(item["unit"]) if item["unit"] in UNIDADES else 0
                    unidad   = st.selectbox("Unidad", UNIDADES, index=u_idx)
                    c_idx    = CATEGORIAS_INSUMOS.index(item["category"]) if item["category"] in CATEGORIAS_INSUMOS else len(CATEGORIAS_INSUMOS) - 1
                    categoria = st.selectbox("Categoría", CATEGORIAS_INSUMOS, index=c_idx)
                with col2:
                    stock_min = st.number_input(
                        "Mínimo de alerta",
                        value=float(item["stock_min"]), min_value=0.0, step=0.5,
                        help="Cuando el stock baje de este número te aparecerá una alerta",
                    )
                    costo = st.number_input(
                        "Costo por unidad (💲)",
                        value=float(item["cost_per_unit"]), min_value=0.0, step=100.0,
                    )
                    st.metric("Stock actual", f"{_fmt(item['stock_current'])} {item['unit']}")

                col_g, col_e = st.columns(2)
                with col_g:
                    guardar  = st.form_submit_button("💾 Guardar", use_container_width=True)
                with col_e:
                    eliminar = st.form_submit_button("🗑️ Eliminar", use_container_width=True)

            if guardar:
                actualizar_ingrediente(item["id"], {
                    "name": nombre, "unit": unidad, "category": categoria,
                    "stock_min": stock_min, "cost_per_unit": costo,
                })
                st.success("Guardado.")
                st.rerun()

            if eliminar:
                eliminar_ingrediente(item["id"])
                st.rerun()


def _form_nuevo_insumo(restaurante: dict):
    with st.form("form_nuevo"):
        st.markdown("#### Nuevo insumo")
        st.caption("Define el producto. El stock arranca en 0 — luego usas **Llegó mercancía** para cargarlo.")
        col1, col2 = st.columns(2)
        with col1:
            nombre    = st.text_input("Nombre *", placeholder="Ej: Pechuga de pollo")
            categoria = st.selectbox("Categoría *", CATEGORIAS_INSUMOS)
        with col2:
            unidad    = st.selectbox(
                "¿En qué se mide? *", UNIDADES,
                help="kg = kilos, lt = litros, und = unidades (huevos, limones...)",
            )
            stock_min = st.number_input(
                "¿Cuándo quieres que te avise? (mínimo)",
                min_value=0.0, step=0.5, value=1.0,
                help="Si tienes menos de este número, aparece una alerta en rojo/amarillo",
            )
            costo = st.number_input(
                "¿Cuánto te cuesta por unidad? (💲)",
                min_value=0.0, step=100.0,
            )

        col_g, col_c = st.columns(2)
        with col_g:
            guardar  = st.form_submit_button("Crear insumo", type="primary", use_container_width=True)
        with col_c:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)

    if guardar:
        if not nombre.strip():
            st.error("El nombre es obligatorio.")
        else:
            crear_ingrediente(restaurante["id"], nombre.strip(), unidad,
                              stock_min, costo, categoria)
            st.session_state["stock_form_nuevo"] = False
            st.success(f"✅ '{nombre}' creado. Ahora ve a **📦 Inventario → Llegó mercancía** para cargar el stock inicial.")
            st.rerun()

    if cancelar:
        st.session_state["stock_form_nuevo"] = False
        st.rerun()


# ── Tab 3: Historial ───────────────────────────────────────────────────────────

def _tab_historial(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("Sin movimientos aún.")
        return

    st.markdown("### Todo lo que ha pasado con tu inventario")
    st.caption("Aquí queda el registro de cada compra, descarte o ajuste que hayas hecho.")

    col1, col2 = st.columns(2)
    with col1:
        ops_ing = {"Todos los insumos": None}
        ops_ing.update({i["name"]: i["id"] for i in ingredientes})
        ing_sel = st.selectbox("Insumo", list(ops_ing.keys()), key="hist_ing")
        ing_id  = ops_ing[ing_sel]
    with col2:
        ETIQUETAS = {
            "Todos": "Todos",
            "entrada": "📥 Llegó mercancía",
            "merma":   "🗑️ Se dañó o venció",
            "ajuste":  "🔢 Conteo / ajuste",
            "salida":  "📤 Salida especial",
        }
        tipo_sel = st.selectbox("Tipo de movimiento", list(ETIQUETAS.values()), key="hist_tipo")
        tipo_key = [k for k, v in ETIQUETAS.items() if v == tipo_sel][0]

    movs = obtener_movimientos(restaurante["id"], ing_id, limit=200)
    if tipo_key != "Todos":
        movs = [m for m in movs if m["type"] == tipo_key]

    if not movs:
        st.info("No hay movimientos con esos filtros.")
        return

    # KPIs
    entradas = sum(float(m["quantity"]) for m in movs if m["type"] == "entrada")
    mermas   = sum(abs(float(m["quantity"])) for m in movs if m["type"] == "merma")
    col_e, col_m, col_t = st.columns(3)
    with col_e:
        st.metric("📥 Total comprado", f"{_fmt(entradas)}")
    with col_m:
        st.metric("🗑️ Total descartado", f"{_fmt(mermas)}")
    with col_t:
        st.metric("📋 Registros", len(movs))

    st.divider()

    filas = []
    for m in movs:
        fecha_col = datetime.fromisoformat(
            m["created_at"].replace("Z", "+00:00")
        ).astimezone(COL_TZ)
        ing_data  = m.get("ingredients") or {}
        cantidad  = float(m["quantity"])
        signo     = "+" if cantidad >= 0 else ""
        etiqueta  = {
            "entrada": "📥 Compra",
            "merma":   "🗑️ Descarte",
            "ajuste":  "🔢 Conteo",
            "salida":  "📤 Salida",
        }.get(m["type"], m["type"])

        filas.append({
            "Fecha":   fecha_col.strftime("%d/%m/%Y %H:%M"),
            "Insumo":  ing_data.get("name", "—"),
            "Qué pasó": etiqueta,
            "Cantidad": f"{signo}{_fmt(cantidad)} {ing_data.get('unit', '')}",
            "Detalle":  m.get("reason") or "—",
            "Precio/u": f"💲{float(m['cost_per_unit']):,.0f}" if m.get("cost_per_unit") else "—",
        })

    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _fmt(valor) -> str:
    v = float(valor)
    return f"{v:.0f}" if v == int(v) else f"{v:.2f}".rstrip("0")
