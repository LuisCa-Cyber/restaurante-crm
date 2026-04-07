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
    st.markdown("### 🤖 Asistente del restaurante")
    st.caption("Pregunta sobre ventas, inventario, meseros o cualquier dato del negocio.")

    if "chat_historial" not in st.session_state:
        st.session_state["chat_historial"] = []

    # Sugerencias rápidas
    if not st.session_state["chat_historial"]:
        st.markdown("**Puedes preguntarme cosas como:**")
        cols = st.columns(3)
        for idx, pregunta in enumerate(PREGUNTAS_SUGERIDAS):
            with cols[idx % 3]:
                if st.button(pregunta, use_container_width=True, key=f"sug_{idx}"):
                    _procesar(restaurante, pregunta)

        st.divider()

    # Historial de mensajes
    for msg in st.session_state["chat_historial"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta..."):
        _procesar(restaurante, prompt)


def _procesar(restaurante: dict, pregunta: str):
    restaurant_id = restaurante["id"]

    # Mostrar mensaje usuario
    st.session_state["chat_historial"].append({"role": "user", "content": pregunta})

    with st.spinner("Consultando datos..."):
        try:
            respuesta = chat(
                restaurant_id=restaurant_id,
                historial=st.session_state["chat_historial"][:-1],
                mensaje_usuario=pregunta,
            )
        except Exception as e:
            respuesta = f"❌ Error al consultar: {e}"

    st.session_state["chat_historial"].append({"role": "assistant", "content": respuesta})
    st.rerun()
