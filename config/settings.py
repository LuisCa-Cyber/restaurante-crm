# config/settings.py — Configuración global y carga de variables de entorno

import streamlit as st
import os
from dotenv import load_dotenv

# Carga .env en desarrollo local (en producción usa Streamlit Secrets)
load_dotenv()


def get_env(key: str) -> str:
    """
    Lee una variable de entorno.
    - Local: usa .env cargado por python-dotenv (evita el warning de secrets)
    - Streamlit Cloud: usa st.secrets (no hay .env en producción)
    """
    # Primero intenta .env / variables del sistema (local)
    valor = os.getenv(key)
    if valor:
        return valor
    # Si no está, intenta Streamlit Secrets (producción)
    try:
        return st.secrets[key]
    except Exception:
        raise ValueError(f"Variable de entorno '{key}' no encontrada en .env ni en Streamlit Secrets.")


def configurar_pagina():
    """Configura el layout y metadatos globales de la app."""
    st.set_page_config(
        page_title="RestauranteCRM",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
