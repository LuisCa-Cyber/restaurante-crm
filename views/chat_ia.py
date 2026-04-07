# views/chat_ia.py — Módulo de chat con IA

import json
import streamlit as st
from ai.agent import chat
from database.chat_db import guardar_sesion, obtener_sesiones, eliminar_sesion

PREGUNTAS_SUGERIDAS = [
    "¿Cuánto vendimos esta semana?",
    "¿Cuál es el plato más vendido del mes?",
    "¿Qué mesero ha vendido más?",
    "¿Qué insumos están en estado crítico?",
    "¿Cuánto me ha costado lo que se ha dañado?",
    "Dame un resumen de los últimos 7 días",
]


def mostrar_chat(restaurante: dict):
    if "chat_historial" not in st.session_state:
        st.session_state["chat_historial"] = []

    col_chat, col_hist = st.columns([3, 1])

    with col_hist:
        _panel_historial(restaurante)

    with col_chat:
        _panel_chat(restaurante)


# ── Panel de chat ─────────────────────────────────────────────────────────────

def _panel_chat(restaurante: dict):
    col_titulo, col_btn = st.columns([4, 1])
    with col_titulo:
        st.markdown("### 🤖 Asistente del restaurante")
        st.caption("Pregunta sobre ventas, inventario, meseros o cualquier dato del negocio.")
    with col_btn:
        st.markdown("")
        if st.button("🔄 Nuevo chat", use_container_width=True):
            _guardar_y_limpiar(restaurante)

    if not st.session_state["chat_historial"]:
        st.markdown("**Puedes preguntarme cosas como:**")
        cols = st.columns(3)
        for idx, pregunta in enumerate(PREGUNTAS_SUGERIDAS):
            with cols[idx % 3]:
                if st.button(pregunta, use_container_width=True, key=f"sug_{idx}"):
                    _procesar(restaurante, pregunta)
        st.divider()

    for msg in st.session_state["chat_historial"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu pregunta..."):
        _procesar(restaurante, prompt)


# ── Panel de historial ────────────────────────────────────────────────────────

def _panel_historial(restaurante: dict):
    st.markdown("### 🕘 Historial")

    # Guardar conversación activa si tiene mensajes y se hizo scroll al historial
    historial_actual = st.session_state.get("chat_historial", [])
    if historial_actual:
        st.caption("**Conversación actual**")
        titulo_actual = next(
            (m["content"][:50] for m in historial_actual if m["role"] == "user"), "Sin título"
        )
        num_preguntas = sum(1 for m in historial_actual if m["role"] == "user")
        st.info(f"💬 {titulo_actual}{'...' if len(titulo_actual)==50 else ''}\n\n_{num_preguntas} pregunta(s)_")
        st.divider()

    sesiones = obtener_sesiones(restaurante["id"])

    if not sesiones:
        st.caption("Aquí aparecerán tus conversaciones guardadas.")
        return

    st.caption(f"{len(sesiones)} conversación(es) guardada(s)")

    for s in sesiones:
        fecha = s["created_at"][:10]
        titulo = s["titulo"][:40] + ("..." if len(s["titulo"]) > 40 else "")
        mensajes = json.loads(s["mensajes"]) if isinstance(s["mensajes"], str) else s["mensajes"]
        num_q = sum(1 for m in mensajes if m["role"] == "user")

        with st.expander(f"🗂️ {titulo}"):
            st.caption(f"📅 {fecha}  |  {num_q} pregunta(s)")
            col_c, col_e = st.columns(2)
            with col_c:
                if st.button("Cargar", key=f"cargar_{s['id']}", use_container_width=True):
                    _guardar_y_limpiar(restaurante)
                    st.session_state["chat_historial"] = mensajes
                    st.rerun()
            with col_e:
                if st.button("🗑️", key=f"del_{s['id']}", use_container_width=True,
                             help="Eliminar esta conversación"):
                    eliminar_sesion(s["id"])
                    st.rerun()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _guardar_y_limpiar(restaurante: dict):
    historial = st.session_state.get("chat_historial", [])
    if historial:
        titulo = next(
            (m["content"][:80] for m in historial if m["role"] == "user"), "Conversación"
        )
        guardar_sesion(restaurante["id"], titulo, historial)
    st.session_state["chat_historial"] = []
    st.rerun()


def _procesar(restaurante: dict, pregunta: str):
    st.session_state["chat_historial"].append({"role": "user", "content": pregunta})

    with st.spinner("Consultando datos..."):
        try:
            respuesta = chat(
                restaurant_id=restaurante["id"],
                historial=st.session_state["chat_historial"][:-1],
                mensaje_usuario=pregunta,
            )
        except Exception as e:
            respuesta = f"❌ Error al consultar: {e}"

    st.session_state["chat_historial"].append({"role": "assistant", "content": respuesta})
    st.rerun()
