# views/chat_ia.py — Módulo de chat con IA

import streamlit as st
from ai.agent import chat

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
    if "chat_sesiones" not in st.session_state:
        st.session_state["chat_sesiones"] = []  # lista de conversaciones pasadas

    col_chat, col_hist = st.columns([3, 1])

    with col_hist:
        _panel_historial()

    with col_chat:
        _panel_chat(restaurante)


def _panel_chat(restaurante: dict):
    col_titulo, col_btn = st.columns([4, 1])
    with col_titulo:
        st.markdown("### 🤖 Asistente del restaurante")
        st.caption("Pregunta sobre ventas, inventario, meseros o cualquier dato del negocio.")
    with col_btn:
        st.markdown("")
        if st.button("🔄 Nuevo chat", use_container_width=True):
            _guardar_sesion_actual()
            st.session_state["chat_historial"] = []
            st.rerun()

    # Sugerencias rápidas cuando no hay historial
    if not st.session_state["chat_historial"]:
        st.markdown("**Puedes preguntarme cosas como:**")
        cols = st.columns(3)
        for idx, pregunta in enumerate(PREGUNTAS_SUGERIDAS):
            with cols[idx % 3]:
                if st.button(pregunta, use_container_width=True, key=f"sug_{idx}"):
                    _procesar(restaurante, pregunta)
        st.divider()

    # Mensajes de la conversación actual
    for msg in st.session_state["chat_historial"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu pregunta..."):
        _procesar(restaurante, prompt)


def _panel_historial():
    st.markdown("### 🕘 Historial")

    sesiones = st.session_state.get("chat_sesiones", [])

    # Guardar sesión activa si tiene mensajes (para mostrarla en historial)
    historial_actual = st.session_state.get("chat_historial", [])

    if not sesiones and not historial_actual:
        st.caption("Aquí aparecerán tus conversaciones anteriores.")
        return

    # Conversación activa
    if historial_actual:
        primer_msg = next((m["content"] for m in historial_actual if m["role"] == "user"), "Conversación actual")
        with st.expander(f"💬 {primer_msg[:40]}...", expanded=False):
            st.caption(f"{len([m for m in historial_actual if m['role'] == 'user'])} preguntas")

    # Conversaciones pasadas
    for idx, sesion in enumerate(reversed(sesiones)):
        primer_msg = sesion["titulo"]
        num_preguntas = sesion["preguntas"]
        with st.expander(f"🗂️ {primer_msg[:35]}...", expanded=False):
            st.caption(f"{num_preguntas} preguntas")
            if st.button("Cargar", key=f"cargar_{idx}", use_container_width=True):
                _guardar_sesion_actual()
                st.session_state["chat_historial"] = sesion["mensajes"]
                st.rerun()


def _guardar_sesion_actual():
    historial = st.session_state.get("chat_historial", [])
    if not historial:
        return
    primer_msg = next((m["content"] for m in historial if m["role"] == "user"), "Conversación")
    num_preguntas = len([m for m in historial if m["role"] == "user"])
    st.session_state["chat_sesiones"].append({
        "titulo": primer_msg,
        "preguntas": num_preguntas,
        "mensajes": historial.copy(),
    })


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
