# config/settings.py — Configuración global y carga de variables de entorno

import streamlit as st
import os

# Carga .env solo en desarrollo local (en Streamlit Cloud no existe este módulo)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


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
        page_title="Gestión Restaurante",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
