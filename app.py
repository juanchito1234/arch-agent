import os

import streamlit as st

from agent.agent import ArchitectureAgent
from chat import service as chat_service
from config.settings import (
    GROQ_API_KEY,
    GROQ_MODELS,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)
from diagram import (
    inject_diagram_styles,
    render_message_with_diagrams,
    render_diagram_canvas_view,
    extract_mermaid_blocks,
)


# ============================================================
# Configuración de Streamlit
# ============================================================

st.set_page_config(
    page_title="Architecture Recommendation Agent",
    page_icon="🏗️",
    layout="wide"
)


# ============================================================
# Inicialización
# ============================================================

chat_service.initialize_chat()
inject_diagram_styles()


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("⚙️ Configuración")

    # API Key
    api_key_input = st.text_input(
        "Groq API Key",
        value=GROQ_API_KEY,
        type="password",
        help=(
            "Si se deja vacío se utilizará la API Key definida "
            "en el archivo .env."
        )
    )

    # Modelo
    selected_model = st.selectbox(
        "Selecciona el Modelo de Groq",
        options=GROQ_MODELS,
        index=GROQ_MODELS.index(DEFAULT_MODEL)
        if DEFAULT_MODEL in GROQ_MODELS else 0
    )

    # Tokens
    max_tokens_input = st.slider(
        "Límite máximo de Tokens de Respuesta",
        min_value=256,
        max_value=16384,
        value=DEFAULT_MAX_TOKENS,
        step=256,
        help=(
            "Controla qué tan larga puede ser "
            "la respuesta generada por el modelo."
        )
    )

    # Temperatura
    temperature_input = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=2.0,
        value=DEFAULT_TEMPERATURE,
        step=0.1,
        help=(
            "Controla la variabilidad de las respuestas "
            "generadas por el modelo."
        )
    )

    st.markdown("---")

    # ========================================================
    # Historial de conversaciones
    # ========================================================

    st.title("💬 Historial de Conversaciones")

    if st.button(
        "➕ Nueva Conversación",
        use_container_width=True
    ):
        new_id = chat_service.create_new_session()

        st.session_state["current_session_id"] = new_id

        st.rerun()

    sessions = chat_service.get_sessions()

    # Crear sesión inicial si no existe ninguna
    if not sessions:
        initial_id = chat_service.create_new_session()
        sessions = chat_service.get_sessions()

    # Seleccionar sesión actual
    if "current_session_id" not in st.session_state:
        st.session_state["current_session_id"] = sessions[0][0]

    # Mostrar sesiones
    for session_id, session_title in sessions:

        col1, col2 = st.columns([0.8, 0.2])

        is_active = (
            session_id == st.session_state["current_session_id"]
        )

        button_label = (
            f"{'👉 ' if is_active else ''}{session_title}"
        )

        if col1.button(
            button_label,
            key=f"session_{session_id}",
            use_container_width=True
        ):
            st.session_state["current_session_id"] = session_id
            st.rerun()

        if col2.button(
            "🗑️",
            key=f"delete_{session_id}"
        ):
            chat_service.delete_session(session_id)

            if (
                st.session_state["current_session_id"]
                == session_id
            ):
                remaining_sessions = chat_service.get_sessions()

                if remaining_sessions:
                    st.session_state["current_session_id"] = (
                        remaining_sessions[0][0]
                    )
                else:
                    st.session_state["current_session_id"] = (
                        chat_service.create_new_session()
                    )

            st.rerun()

    # Acceso rápido a diagramas de la sesión actual
    current_sess_id = st.session_state.get("current_session_id")
    if current_sess_id:
        current_sess_msgs = chat_service.get_session_messages(current_sess_id)
        has_diagrams = any(
            m.get("role") == "assistant" and "```mermaid" in m.get("content", "").lower()
            for m in current_sess_msgs
        )
        if has_diagrams:
            st.markdown("---")
            st.markdown("##### 📐 Diagrama Activo")
            st.caption("Diagrama de arquitectura generado en esta sesión.")
            if st.button("🖥️ Abrir Modo Estudio", use_container_width=True, key="sidebar_open_studio_btn"):
                for m in reversed(current_sess_msgs):
                    if m.get("role") == "assistant" and "```mermaid" in m.get("content", "").lower():
                        blocks = extract_mermaid_blocks(m["content"])
                        if blocks:
                            st.session_state["fullscreen_diagram"] = blocks[0]
                            st.session_state["fullscreen_title"] = "Diagrama de Arquitectura"
                            st.rerun()
                        break


# ============================================================
# Interfaz principal
# ============================================================

# Si el usuario activó la vista de pantalla completa / estudio
if st.session_state.get("fullscreen_diagram"):
    render_diagram_canvas_view()
    st.stop()

st.header(
    "🏗️ Agente Recomendador de Arquitecturas de Software"
)

st.caption(
    "Proporciona tus historias de usuario o el contexto de "
    "tu aplicación para recibir recomendaciones de arquitectura con diagramas interactivos."
)


# ============================================================
# Sesión actual
# ============================================================

current_session_id = st.session_state["current_session_id"]

messages = chat_service.get_session_messages(
    current_session_id
)


# ============================================================
# Renderizar historial
# ============================================================

for idx, message in enumerate(messages):
    render_message_with_diagrams(message, idx)


# ============================================================
# Entrada del usuario
# ============================================================

user_input = st.chat_input(
    "Escribe el contexto de tu proyecto o pega tus historias de usuario..."
)


if user_input:

    # --------------------------------------------------------
    # Mostrar y guardar mensaje del usuario
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.markdown(user_input)

    chat_service.add_message(
        current_session_id,
        "user",
        user_input
    )

    # --------------------------------------------------------
    # Actualizar título de la conversación
    # --------------------------------------------------------

    if len(messages) == 0:

        new_title = chat_service.generate_session_title(
            user_input
        )

        chat_service.update_session_title(
            current_session_id,
            new_title
        )

    # --------------------------------------------------------
    # Obtener API Key
    # --------------------------------------------------------

    effective_api_key = (
        api_key_input.strip()
        if api_key_input.strip()
        else os.getenv("GROQ_API_KEY", "")
    )

    if not effective_api_key:

        st.error(
            "No se encontró una API Key válida de Groq. "
            "Por favor ingrésala en la barra lateral o "
            "configúrala en el archivo .env."
        )

    else:

        # ----------------------------------------------------
        # Crear agente
        # ----------------------------------------------------

        agent = ArchitectureAgent(
            api_key=effective_api_key,
            model=selected_model,
            max_tokens=max_tokens_input,
            temperature=temperature_input,
        )

        # ----------------------------------------------------
        # Generar respuesta
        # ----------------------------------------------------

        try:

            with st.chat_message("assistant"):

                message_placeholder = st.empty()

                full_response = ""

                completion = agent.generate_response(
                    history=messages,
                    user_input=user_input
                )

                for chunk in completion:

                    content = (
                        chunk.choices[0].delta.content
                        or ""
                    )

                    full_response += content

                    message_placeholder.markdown(
                        full_response + "▌"
                    )

                message_placeholder.markdown(
                    full_response
                )

            # ------------------------------------------------
            # Guardar respuesta
            # ------------------------------------------------

            chat_service.add_message(
                current_session_id,
                "assistant",
                full_response
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error al comunicar con la API de Groq: {str(e)}"
            )