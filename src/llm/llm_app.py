"""Interfaz Streamlit para interactuar con TinyLlama vía Ollama.

Ejecutar:
    streamlit run src/llm/llm_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar directamente sin instalar el paquete
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

from src.config import load_settings
from src.llm.ollama_client import OllamaConfig, TinyLlamaClient, load_role
from src.llm.stub import StubLlamaClient

# ---------- Configuración de página ----------
st.set_page_config(page_title="NAIRA · LLM Chat", page_icon="🌱", layout="wide")
st.title("NAIRA · Chat con TinyLlama")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Conexión")

    cfg = load_settings()

    sim_mode = st.toggle("Modo simulado", value=cfg.sim_mode)
    host = st.text_input("Host Ollama", value=cfg.ollama_host, disabled=sim_mode)
    port = st.number_input("Puerto", value=cfg.ollama_port, min_value=1, max_value=65535, disabled=sim_mode)
    model = st.text_input("Modelo", value=cfg.ollama_model, disabled=sim_mode)
    timeout = st.slider("Timeout (s)", 5, 300, int(cfg.ollama_timeout_s), disabled=sim_mode)
    num_ctx = st.select_slider(
        "Contexto (tokens)",
        options=[512, 1024, 2048, 4096, 8192, 16384],
        value=cfg.ollama_num_ctx,
        disabled=sim_mode,
    )

    st.divider()

    # Estado de conexión
    if sim_mode:
        st.success("Simulado — sin Ollama")
        _client_ready = True
    else:
        ollama_cfg = OllamaConfig(host=host, port=port, model=model, timeout_s=float(timeout))
        _check_client = TinyLlamaClient(config=ollama_cfg)
        _client_ready = _check_client.is_model_ready()
        if _client_ready:
            st.success(f"Modelo `{model}` disponible")
        else:
            st.error(f"Modelo `{model}` no encontrado en {host}:{port}")
            if st.button("Descargar modelo"):
                with st.spinner("Descargando…"):
                    ok = _check_client.ensure_model_available()
                st.success("Descargado") if ok else st.error("No se pudo descargar")
                st.rerun()

    st.divider()
    st.caption("Variables de entorno:\nNAIRA_OLLAMA_HOST / PORT / MODEL")

# ---------- Inicializar estado ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = ""
if "role" not in st.session_state:
    st.session_state.role = load_role(cfg.ollama_role_path)

# ---------- Panel de rol ----------
with st.expander("Rol del modelo", expanded=False):
    st.caption(f"Cargado desde: `{cfg.ollama_role_path}` · Variable: `NAIRA_OLLAMA_ROLE_PATH`")
    role_input = st.text_area(
        "Rol",
        value=st.session_state.role,
        height=200,
        label_visibility="collapsed",
    )
    if role_input != st.session_state.role:
        st.session_state.role = role_input
        st.rerun()

# ---------- Panel de contexto ----------
with st.expander("Contexto / Datos", expanded=not st.session_state.context == ""):
    st.caption("Pega aquí los datos que quieres que el modelo tenga en cuenta (JSON, CSV, texto libre…). Se incluirá automáticamente en cada consulta.")
    context_input = st.text_area(
        "Contexto",
        value=st.session_state.context,
        height=180,
        placeholder="Ejemplo:\ntemperatura: 34.2°C\nhumedad_suelo: 18%\ncaudal: 0.0 l/min",
        label_visibility="collapsed",
    )
    if context_input != st.session_state.context:
        st.session_state.context = context_input
        st.rerun()

# ---------- Mostrar historial ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Input del usuario ----------
if prompt := st.chat_input("Escribe tu consulta…", disabled=not _client_ready):
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construir prompt completo con contexto
    if st.session_state.context.strip():
        full_prompt = (
            f"Contexto:\n{st.session_state.context.strip()}\n\n"
            f"Pregunta: {prompt}"
        )
    else:
        full_prompt = prompt

    # Construir cliente según modo
    if sim_mode:
        client = StubLlamaClient()
    else:
        client = TinyLlamaClient(config=OllamaConfig(
            host=host, port=port, model=model, timeout_s=float(timeout)
        ))

    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Generando…"):
            try:
                response = client.generate(
                    full_prompt,
                    system=st.session_state.role or None,
                    options={"num_ctx": num_ctx} if not sim_mode else None,
                )
            except RuntimeError as exc:
                response = f"Error al contactar con Ollama: {exc}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# ---------- Botón para limpiar chat ----------
if st.session_state.messages:
    if st.button("Limpiar chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()
