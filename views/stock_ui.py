# pages/stock_ui.py — Módulo de Stock / Inventario

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone, timedelta

from database.stock_db import (
    CATEGORIAS_INSUMOS, UNIDADES, nivel_alerta,
    obtener_ingredientes, crear_ingrediente, actualizar_ingrediente,
    eliminar_ingrediente, registrar_movimiento, obtener_movimientos,
    valor_total_inventario,
)

COL_TZ = timezone(timedelta(hours=-5))

ACCIONES = {
    "llegó": {
        "tipo":   "entrada",
        "titulo": "📥 Llegó mercancía",
        "desc":   "Registra una compra o entrega de proveedor",
    },
    "salió": {
        "tipo":   "salida",
        "titulo": "📤 Salió mercancía",
        "desc":   "Registra lo que usaste hoy en cocina",
    },
    "dañó": {
        "tipo":   "merma",
        "titulo": "🗑️ Se dañó o venció",
        "desc":   "Producto que hay que tirar",
    },
    "conté": {
        "tipo":   "ajuste",
        "titulo": "🔢 Hice un conteo",
        "desc":   "Ajusta el stock al número real que contaste en bodega",
    },
}

ICONO = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}


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


def mostrar_analisis_stock(restaurante: dict):
    """Expuesto para usarse desde el Dashboard."""
    _tab_analisis(restaurante)


# ── Tab 1: Inventario ─────────────────────────────────────────────────────────

def _tab_inventario(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])

    if not ingredientes:
        st.info("Aún no tienes insumos registrados.")
        st.markdown("Ve a **🥩 Mis insumos** y crea los productos que manejas en cocina.")
        return

    accion_activa = st.session_state.get("stock_accion")
    if accion_activa:
        # Para salida/merma solo mostrar los que tienen stock > 0
        if accion_activa in ("salió", "dañó"):
            lista_accion = [i for i in ingredientes if float(i["stock_current"]) > 0]
            if not lista_accion:
                st.warning("No hay insumos con stock disponible para registrar esta acción.")
                st.session_state.pop("stock_accion", None)
                st.rerun()
                return
        else:
            lista_accion = ingredientes
        _formulario_accion(restaurante, lista_accion, accion_activa)
        return

    # ── Botones de acción ─────────────────────────────────────────────────────
    st.markdown("### ¿Qué pasó hoy con el inventario?")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📥 Llegó mercancía", use_container_width=True,
                     help="Registra una compra o entrega de proveedor",
                     type="primary"):
            st.session_state["stock_accion"] = "llegó"
            st.rerun()
    with col2:
        if st.button("📤 Salió mercancía", use_container_width=True,
                     help="Registra lo que usaste hoy en cocina"):
            st.session_state["stock_accion"] = "salió"
            st.rerun()
    with col3:
        if st.button("🗑️ Se dañó o venció", use_container_width=True,
                     help="Producto que hay que tirar"):
            st.session_state["stock_accion"] = "dañó"
            st.rerun()
    with col4:
        if st.button("🔢 Hice un conteo", use_container_width=True,
                     help="Ajusta el stock al número real que contaste"):
            st.session_state["stock_accion"] = "conté"
            st.rerun()

    st.divider()

    # ── Filtro de categoría (arriba de todo) ─────────────────────────────────
    cats    = ["Todas"] + sorted(set(i["category"] for i in ingredientes))
    cat_sel = st.selectbox("Filtrar por categoría", cats, key="inv_cat")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    rojos     = [i for i in ingredientes if nivel_alerta(i) == "rojo"]
    amarillos = [i for i in ingredientes if nivel_alerta(i) == "amarillo"]
    valor     = valor_total_inventario(restaurante["id"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Insumos", len(ingredientes))
    with col2:
        st.metric("💰 Valor en bodega", f"💲{valor:,.0f}")
    with col3:
        st.metric("🟡 Reposición pronto", len(amarillos))
    with col4:
        st.metric("🔴 Reponer urgente", len(rojos))

    # ── Alertas agrupadas por categoría ──────────────────────────────────────
    alertas = rojos + amarillos
    if cat_sel != "Todas":
        alertas = [i for i in alertas if i["category"] == cat_sel]

    if alertas:
        st.divider()
        st.markdown("### ⚠️ Necesitan atención")
        cats_alerta = sorted(set(i["category"] for i in alertas))
        for cat in cats_alerta:
            st.markdown(f"#### {cat}")
            for i in [x for x in alertas if x["category"] == cat]:
                alerta = nivel_alerta(i)
                if alerta == "rojo":
                    st.error(
                        f"🔴 **{i['name']}** — "
                        f"{_fmt(i['stock_current'])} {i['unit']} disponibles  |  "
                        f"Crítico: {_fmt(i['stock_critical'])} {i['unit']}"
                    )
                else:
                    minimo = float(i["stock_min"])
                    pct    = float(i["stock_current"]) / minimo * 100 if minimo > 0 else 0
                    st.warning(
                        f"🟡 **{i['name']}** — "
                        f"{_fmt(i['stock_current'])} {i['unit']} disponibles  |  "
                        f"Mínimo: {_fmt(i['stock_min'])} {i['unit']}  |  {pct:.0f}% del mínimo"
                    )
                    st.progress(min(pct / 100, 1.0))
    else:
        st.success("✅ Todo el inventario está sobre el mínimo.")

    # ── Estado actual agrupado por categoría ─────────────────────────────────
    st.divider()
    st.markdown("### Estado actual")

    lista = ingredientes if cat_sel == "Todas" else [i for i in ingredientes if i["category"] == cat_sel]
    cats_lista = sorted(set(i["category"] for i in lista))

    for cat in cats_lista:
        st.markdown(f"#### {cat}")
        hdr = st.columns([3, 2, 2, 2])
        for col, txt in zip(hdr, ["Insumo", "Stock actual", "Costo / unidad", "Valor en bodega"]):
            col.caption(txt)
        for item in [x for x in lista if x["category"] == cat]:
            stock      = float(item["stock_current"])
            alerta     = nivel_alerta(item)
            icono      = ICONO[alerta]
            valor_item = stock * float(item["cost_per_unit"])
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"{icono} **{item['name']}**")
            with col2:
                st.markdown(f"**{_fmt(item['stock_current'])} {item['unit']}**")
                st.caption(f"Mín: {_fmt(item['stock_min'])}  |  Crítico: {_fmt(item['stock_critical'])}")
            with col3:
                st.markdown(f"💲{float(item['cost_per_unit']):,.0f}/{item['unit']}")
            with col4:
                st.markdown(f"💰 💲{valor_item:,.0f}")
        st.divider()


# ── Formulario de acción ──────────────────────────────────────────────────────

def _formulario_accion(restaurante: dict, ingredientes: list, accion: str):
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

    presel     = st.session_state.pop("stock_ing_presel", None)
    ids        = [i["id"] for i in ingredientes]
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
    ing         = next(i for i in ingredientes if i["id"] == ing_id)
    stock_actual = float(ing["stock_current"])
    costo_actual = float(ing["cost_per_unit"])
    alerta       = nivel_alerta(ing)

    st.info(
        f"{ICONO[alerta]} **{ing['name']}** — "
        f"hay **{_fmt(stock_actual)} {ing['unit']}** en bodega  |  "
        f"Costo actual: 💲{costo_actual:,.0f}/{ing['unit']}"
    )
    st.divider()

    with st.form("form_accion_stock"):
        if accion == "llegó":
            st.markdown("**¿Cuánto llegó?**")
            col1, col2 = st.columns(2)
            with col1:
                cantidad = st.number_input(
                    f"Cantidad ({ing['unit']})", min_value=0.01, step=0.5,
                )
            with col2:
                costo = st.number_input(
                    "Precio que pagaste por unidad (💲)",
                    min_value=0.0, step=100.0, value=costo_actual,
                    help="Si el precio cambió, actualízalo aquí",
                )
            motivo  = st.text_input("¿De dónde viene? (opcional)",
                                    placeholder="Ej: Frigorífico Andino, plaza de mercado...")
            enviado = st.form_submit_button("✅ Registrar entrada", type="primary",
                                            use_container_width=True)

        elif accion == "salió":
            st.markdown("**¿Cuánto se usó hoy?**")
            cantidad = st.number_input(
                f"Cantidad usada ({ing['unit']})", min_value=0.01, step=0.5,
                help=f"Tienes {_fmt(stock_actual)} {ing['unit']} en bodega",
            )
            # Preview del costo proporcional
            if cantidad > 0:
                costo_prop = cantidad * costo_actual
                st.caption(f"💡 Costo equivalente: **💲{costo_prop:,.0f}** "
                           f"({_fmt(cantidad)} × 💲{costo_actual:,.0f})")
            motivo  = st.text_input("¿Para qué se usó? (opcional)",
                                    placeholder="Ej: Servicio del día, preparación almuerzo...")
            enviado = st.form_submit_button("✅ Registrar salida", type="primary",
                                            use_container_width=True)
            costo   = None

        elif accion == "dañó":
            st.markdown("**¿Cuánto hay que tirar?**")
            cantidad = st.number_input(
                f"Cantidad a descartar ({ing['unit']})", min_value=0.01, step=0.5,
            )
            if cantidad > 0:
                costo_prop = cantidad * costo_actual
                st.caption(f"💡 Pérdida equivalente: **💲{costo_prop:,.0f}**")
            motivo  = st.text_input("¿Por qué se dañó? *",
                                    placeholder="Ej: Se venció, se cayó, olía mal...")
            enviado = st.form_submit_button("🗑️ Registrar descarte", type="primary",
                                            use_container_width=True)
            costo   = None

        else:  # conté
            st.markdown("**¿Cuánto contaste en bodega?**")
            st.caption(f"El sistema tiene {_fmt(stock_actual)} {ing['unit']}. "
                       "Si el número real es diferente, escríbelo aquí.")
            cantidad = st.number_input(
                f"Cantidad real contada ({ing['unit']})",
                min_value=0.0, step=0.5, value=stock_actual,
            )
            motivo  = st.text_input("¿Por qué hay diferencia? (opcional)",
                                    placeholder="Ej: Conteo físico de cierre del día...")
            enviado = st.form_submit_button("🔢 Ajustar inventario", type="primary",
                                            use_container_width=True)
            costo   = None

    if enviado:
        if accion == "dañó" and not motivo.strip():
            st.error("Escribe por qué se dañó el producto.")
            return

        registrar_movimiento(
            restaurante["id"], ing_id, cfg["tipo"], cantidad,
            motivo.strip() if motivo else "",
            costo if accion == "llegó" else None,
        )

        ings_nuevo   = obtener_ingredientes(restaurante["id"])
        ing_nuevo    = next(i for i in ings_nuevo if i["id"] == ing_id)
        nuevo_stock  = float(ing_nuevo["stock_current"])

        if accion == "llegó":
            st.success(f"✅ **{ing['name']}** pasó de {_fmt(stock_actual)} a "
                       f"**{_fmt(nuevo_stock)} {ing['unit']}** en bodega.")
        elif accion == "salió":
            costo_prop = cantidad * costo_actual
            st.success(f"✅ Salida registrada. **{ing['name']}** quedó en "
                       f"**{_fmt(nuevo_stock)} {ing['unit']}**  |  "
                       f"Costo equivalente: 💲{costo_prop:,.0f}")
        elif accion == "dañó":
            costo_prop = cantidad * costo_actual
            st.warning(f"🗑️ Descarte registrado. **{ing['name']}** quedó en "
                       f"**{_fmt(nuevo_stock)} {ing['unit']}**  |  "
                       f"Pérdida: 💲{costo_prop:,.0f}")
        else:
            delta  = nuevo_stock - stock_actual
            signo  = "+" if delta >= 0 else ""
            st.success(f"🔢 **{ing['name']}** ajustado a "
                       f"**{_fmt(nuevo_stock)} {ing['unit']}** ({signo}{_fmt(delta)}).")

        st.session_state.pop("stock_accion", None)
        st.session_state.pop("stock_ing_presel", None)
        st.rerun()


# ── Tab 2: Análisis de costos ─────────────────────────────────────────────────

def _tab_analisis(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("Sin datos aún.")
        return

    st.markdown("### 📊 Análisis de costos del inventario")

    # ── Filtro de fechas ──────────────────────────────────────────────────────
    hoy = datetime.now(COL_TZ).date()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_desde = st.date_input("Desde", value=hoy.replace(day=1), key="an_desde")
    with col_f2:
        fecha_hasta = st.date_input("Hasta", value=hoy, key="an_hasta")

    movs_todos = obtener_movimientos(restaurante["id"], limit=5000)

    # Filtrar por rango de fechas
    def en_rango(m):
        ts = m["created_at"][:10]
        return str(fecha_desde) <= ts <= str(fecha_hasta)

    movs = [m for m in movs_todos if en_rango(m)]

    # Calcular resumen con los movimientos filtrados
    invertido = consumo = merma = 0.0
    for m in movs:
        qty = abs(float(m["quantity"]))
        cpu = float(m["cost_per_unit"]) if m.get("cost_per_unit") else 0.0
        if m["type"] == "entrada":   invertido += qty * cpu
        elif m["type"] == "salida":  consumo   += qty * cpu
        elif m["type"] == "merma":   merma     += qty * cpu

    valor = valor_total_inventario(restaurante["id"])

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Valor actual en bodega", f"💲{valor:,.0f}")
    with col2:
        st.metric("📥 Total invertido (compras)", f"💲{invertido:,.0f}")
    with col3:
        st.metric("📤 Costo de lo consumido", f"💲{consumo:,.0f}")
    with col4:
        st.metric("🗑️ Pérdidas por merma", f"💲{merma:,.0f}",
                  delta=f"-💲{merma:,.0f}" if merma > 0 else None,
                  delta_color="inverse")

    st.divider()

    # Gráfica: composición del gasto
    if invertido > 0:
        df_torta = pd.DataFrame({
            "Categoría": ["En bodega", "Consumido", "Mermas"],
            "Valor":     [valor, consumo, merma],
        })
        df_torta = df_torta[df_torta["Valor"] > 0]
        fig = px.pie(df_torta, names="Categoría", values="Valor",
                     title="¿A dónde fue lo que compraste?",
                     color_discrete_sequence=["#2ECC71", "#3498DB", "#E74C3C"])
        fig.update_traces(hovertemplate="<b>%{label}</b><br>💲 %{value:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tabla de costo proporcional por insumo
    st.markdown("#### Costo proporcional por insumo (regla de tres)")
    st.caption("Para cada insumo: cuánto costó lo que ya salió y lo que se dañó, "
               "calculado con el precio de compra vigente.")

    filas = []
    for ing in ingredientes:
        movs_ing = [m for m in movs if m["ingredient_id"] == ing["id"]]

        comprado   = sum(float(m["quantity"]) for m in movs_ing if m["type"] == "entrada")
        costo_comp = sum(
            float(m["quantity"]) * float(m["cost_per_unit"])
            for m in movs_ing if m["type"] == "entrada" and m.get("cost_per_unit")
        )
        consumido  = sum(abs(float(m["quantity"])) for m in movs_ing if m["type"] == "salida")
        costo_cons = sum(
            abs(float(m["quantity"])) * float(m["cost_per_unit"])
            for m in movs_ing if m["type"] == "salida" and m.get("cost_per_unit")
        )
        mermado    = sum(abs(float(m["quantity"])) for m in movs_ing if m["type"] == "merma")
        costo_merm = sum(
            abs(float(m["quantity"])) * float(m["cost_per_unit"])
            for m in movs_ing if m["type"] == "merma" and m.get("cost_per_unit")
        )

        if comprado > 0 or consumido > 0:
            filas.append({
                "Insumo":        ing["name"],
                "Unidad":        ing["unit"],
                "Comprado":      _fmt(comprado),
                "Invertido":     f"💲{costo_comp:,.0f}",
                "Consumido":     _fmt(consumido),
                "Costo consumo": f"💲{costo_cons:,.0f}",
                "Merma":         _fmt(mermado),
                "Pérdida merma": f"💲{costo_merm:,.0f}",
                "En bodega":     f"{_fmt(ing['stock_current'])} {ing['unit']}",
            })

    if filas:
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
    else:
        st.info("Registra compras y salidas para ver el análisis.")

    st.divider()

    # Gráfica de barras: compras por insumo
    st.markdown("#### Inversión por insumo")
    if filas:
        df_bar = pd.DataFrame([
            {"Insumo": f["Insumo"],
             "Invertido": resumen_costos_ing(movs, ing["id"])["invertido"]}
            for f, ing in zip(filas, [i for i in ingredientes
                                       if any(m["ingredient_id"] == i["id"] for m in movs)])
        ])
        df_bar = df_bar[df_bar["Invertido"] > 0].sort_values("Invertido", ascending=False)
        if not df_bar.empty:
            fig2 = px.bar(df_bar, x="Insumo", y="Invertido",
                          title="Total invertido por insumo (💲)",
                          color_discrete_sequence=["#3498DB"],
                          labels={"Invertido": "Pesos invertidos"})
            fig2.update_traces(hovertemplate="<b>%{x}</b><br>💲 %{y:,.0f}<extra></extra>")
            fig2.update_layout(xaxis_tickangle=-30, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)


def resumen_costos_ing(movs: list, ingredient_id: str) -> dict:
    movs_ing = [m for m in movs if m["ingredient_id"] == ingredient_id]
    return {
        "invertido": sum(
            float(m["quantity"]) * float(m["cost_per_unit"])
            for m in movs_ing if m["type"] == "entrada" and m.get("cost_per_unit")
        ),
    }


# ── Tab 3: Mis insumos ─────────────────────────────────────────────────────────

def _tab_insumos(restaurante: dict):
    col_t, col_n = st.columns([4, 1])
    with col_t:
        st.markdown("### Mis insumos")
        st.caption("Define qué productos maneja tu cocina, su unidad y los niveles de alerta.")
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
        cats  = ["Todas"] + sorted(set(i["category"] for i in ingredientes))
        cat_f = st.selectbox("Categoría", cats, key="ins_cat")
    with col_f2:
        busq  = st.text_input("Buscar", placeholder="Nombre del insumo...", key="ins_busq")

    lista = ingredientes
    if cat_f != "Todas":
        lista = [i for i in lista if i["category"] == cat_f]
    if busq:
        lista = [i for i in lista if busq.lower() in i["name"].lower()]

    st.caption(f"{len(lista)} insumo(s)")

    cats_lista = sorted(set(i["category"] for i in lista))
    for cat in cats_lista:
        st.divider()
        st.markdown(f"### {cat}")
        for item in [x for x in lista if x["category"] == cat]:
            alerta = nivel_alerta(item)
            icono  = ICONO[alerta]

            with st.expander(
                f"{icono} **{item['name']}** — "
                f"{_fmt(item['stock_current'])} {item['unit']} en bodega  |  "
                f"Mín 🟡: {_fmt(item['stock_min'])}  |  "
                f"Crítico 🔴: {_fmt(item['stock_critical'])}  |  "
                f"💲{float(item['cost_per_unit']):,.0f}/{item['unit']}"
            ):
                with st.form(f"edit_{item['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre    = st.text_input("Nombre", value=item["name"])
                        u_idx     = UNIDADES.index(item["unit"]) if item["unit"] in UNIDADES else 0
                        unidad    = st.selectbox("Unidad", UNIDADES, index=u_idx)
                        c_idx     = CATEGORIAS_INSUMOS.index(item["category"]) if item["category"] in CATEGORIAS_INSUMOS else len(CATEGORIAS_INSUMOS) - 1
                        categoria = st.selectbox("Categoría", CATEGORIAS_INSUMOS, index=c_idx)
                    with col2:
                        stock_min = st.number_input(
                            "🟡 Mínimo (aviso amarillo)",
                            value=float(item["stock_min"]), min_value=0.0, step=0.5,
                            help="Cuando baje de aquí se pone amarillo",
                        )
                        stock_crit = st.number_input(
                            "🔴 Crítico (aviso rojo)",
                            value=float(item.get("stock_critical") or 0), min_value=0.0, step=0.5,
                            help="Cuando baje de aquí se pone rojo — hay que reponer urgente",
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
                        "stock_min": stock_min, "stock_critical": stock_crit,
                        "cost_per_unit": costo,
                    })
                    st.success("Guardado.")
                    st.rerun()

                if eliminar:
                    eliminar_ingrediente(item["id"])
                    st.rerun()


def _form_nuevo_insumo(restaurante: dict):
    with st.form("form_nuevo"):
        st.markdown("#### Nuevo insumo")
        st.caption("Define el producto. El stock arranca en 0 — usa **Llegó mercancía** para cargarlo.")
        col1, col2 = st.columns(2)
        with col1:
            nombre    = st.text_input("Nombre *", placeholder="Ej: Arroz")
            categoria = st.selectbox("Categoría *", CATEGORIAS_INSUMOS)
            unidad    = st.selectbox(
                "¿En qué se mide? *", UNIDADES,
                index=UNIDADES.index("libra"),
                help="kg=kilos, lt=litros, und=unidades, libra=libras",
            )
        with col2:
            stock_min = st.number_input(
                "🟡 Mínimo (aviso amarillo)",
                min_value=0.0, step=0.5, value=5.0,
                help="Ej: si pones 7 libras, cuando queden 7 o menos se pone amarillo",
            )
            stock_crit = st.number_input(
                "🔴 Crítico (aviso rojo)",
                min_value=0.0, step=0.5, value=2.0,
                help="Ej: si pones 3 libras, cuando queden 3 o menos se pone rojo",
            )
            costo = st.number_input(
                "¿Cuánto te cuesta por unidad? (💲)",
                min_value=0.0, step=100.0,
                help="Usado para calcular el valor del inventario y el costo de lo que sale",
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
                              stock_min, stock_crit, costo, categoria)
            st.session_state["stock_form_nuevo"] = False
            st.success(
                f"✅ '{nombre}' creado. "
                "Ahora ve a **📦 Inventario → Llegó mercancía** para cargar el stock inicial."
            )
            st.rerun()

    if cancelar:
        st.session_state["stock_form_nuevo"] = False
        st.rerun()


# ── Tab 4: Historial ───────────────────────────────────────────────────────────

def _tab_historial(restaurante: dict):
    ingredientes = obtener_ingredientes(restaurante["id"])
    if not ingredientes:
        st.info("Sin movimientos aún.")
        return

    st.markdown("### Todo lo que ha pasado con tu inventario")

    col1, col2 = st.columns(2)
    with col1:
        ops_ing  = {"Todos los insumos": None}
        ops_ing.update({i["name"]: i["id"] for i in ingredientes})
        ing_sel  = st.selectbox("Insumo", list(ops_ing.keys()), key="hist_ing")
        ing_id   = ops_ing[ing_sel]
    with col2:
        ETIQUETAS = {
            "Todos":   "Todos",
            "entrada": "📥 Llegó mercancía",
            "salida":  "📤 Salió mercancía",
            "merma":   "🗑️ Se dañó o venció",
            "ajuste":  "🔢 Conteo / ajuste",
        }
        tipo_sel = st.selectbox("Tipo", list(ETIQUETAS.values()), key="hist_tipo")
        tipo_key = [k for k, v in ETIQUETAS.items() if v == tipo_sel][0]

    movs = obtener_movimientos(restaurante["id"], ing_id, limit=200)
    if tipo_key != "Todos":
        movs = [m for m in movs if m["type"] == tipo_key]

    if not movs:
        st.info("No hay movimientos con esos filtros.")
        return

    # KPIs del historial
    entradas     = sum(float(m["quantity"]) for m in movs if m["type"] == "entrada")
    consumido    = sum(abs(float(m["quantity"])) for m in movs if m["type"] == "salida")
    mermas       = sum(abs(float(m["quantity"])) for m in movs if m["type"] == "merma")
    costo_cons   = sum(
        abs(float(m["quantity"])) * float(m["cost_per_unit"])
        for m in movs if m["type"] == "salida" and m.get("cost_per_unit")
    )
    costo_merma  = sum(
        abs(float(m["quantity"])) * float(m["cost_per_unit"])
        for m in movs if m["type"] == "merma" and m.get("cost_per_unit")
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📥 Comprado", _fmt(entradas))
    with col2:
        st.metric("📤 Consumido", _fmt(consumido))
    with col3:
        st.metric("💲 Costo consumo", f"💲{costo_cons:,.0f}")
    with col4:
        st.metric("🗑️ Mermas", _fmt(mermas))
    with col5:
        st.metric("💲 Pérdida merma", f"💲{costo_merma:,.0f}")

    st.divider()

    filas = []
    for m in movs:
        fecha_col = datetime.fromisoformat(
            m["created_at"].replace("Z", "+00:00")
        ).astimezone(COL_TZ)
        ing_data  = m.get("ingredients") or {}
        cantidad  = float(m["quantity"])
        signo     = "+" if cantidad >= 0 else ""
        cpu       = float(m["cost_per_unit"]) if m.get("cost_per_unit") else 0.0
        costo_total = abs(cantidad) * cpu if cpu else None
        etiqueta  = {
            "entrada": "📥 Compra",
            "salida":  "📤 Consumo",
            "merma":   "🗑️ Descarte",
            "ajuste":  "🔢 Conteo",
        }.get(m["type"], m["type"])

        filas.append({
            "Fecha":        fecha_col.strftime("%d/%m/%Y %H:%M"),
            "Insumo":       ing_data.get("name", "—"),
            "Qué pasó":     etiqueta,
            "Cantidad":     f"{signo}{_fmt(cantidad)} {ing_data.get('unit', '')}",
            "Costo/u":      f"💲{cpu:,.0f}" if cpu else "—",
            "Costo total":  f"💲{costo_total:,.0f}" if costo_total else "—",
            "Detalle":      m.get("reason") or "—",
        })

    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _fmt(valor) -> str:
    v = float(valor)
    return f"{v:.0f}" if v == int(v) else f"{v:.2f}".rstrip("0")
