"""
Componentes visuales y vista interactiva para diagramas de arquitectura en Streamlit.
"""
import streamlit as st
import pandas as pd
from diagram.parser import (
    sanitize_mermaid_code,
    split_content_and_diagrams,
    parse_mermaid_elements,
)


def _render_dataframe(df, hide_index=True):
    try:
        st.dataframe(df, width="stretch", hide_index=hide_index)
    except (TypeError, Exception):
        st.dataframe(df, use_container_width=True, hide_index=hide_index)


def inject_diagram_styles():
    """
    Inyecta estilos CSS modernos para animaciones fluidas, tarjetas de diagramas,
    efectos hover y transiciones de deslizamiento.
    """
    st.markdown(
        """
        <style>
        /* Animación de deslizamiento suave para el cajón lateral / dialog */
        @keyframes slideInRightAnim {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes pulseAccent {
            0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
            70% { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0); }
            100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }

        /* Estilo para el contenedor de diálogo (drawer) */
        div[data-testid="stDialog"] {
            animation: slideInRightAnim 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Tarjeta dinámica del diagrama en el chat */
        .arch-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-bottom: none;
            padding: 10px 16px;
            border-radius: 12px 12px 0 0;
            margin-top: 14px;
        }

        .arch-card-title {
            font-weight: 600;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #818cf8;
        }

        .arch-badge-live {
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            border: 1px solid rgba(99, 102, 241, 0.4);
            animation: pulseAccent 2.5s infinite;
        }

        .arch-diagram-body {
            border: 1px solid rgba(99, 102, 241, 0.25);
            background: rgba(15, 23, 42, 0.3);
            border-radius: 0 0 12px 12px;
            padding: 16px;
            margin-bottom: 16px;
            transition: all 0.25s ease;
        }

        .arch-diagram-body:hover {
            border-color: rgba(99, 102, 241, 0.6);
            box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.2);
        }

        /* Banner de vista de estudio / lienzo completo */
        .studio-banner {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Contenedor del lienzo de zoom */
        .zoom-canvas-container {
            overflow: auto;
            max-height: 75vh;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.15);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def _get_drawer_dialog():
    import inspect
    sig = inspect.signature(st.dialog)
    if "position" in sig.parameters:
        return st.dialog("📐 Inspección Detallada de Arquitectura", position="right", width="large")
    return st.dialog("📐 Inspección Detallada de Arquitectura", width="large")


@_get_drawer_dialog()
def open_diagram_drawer(diagram_code: str, title: str = "Diagrama Conceptual de Arquitectura"):
    """
    Abre un panel lateral deslizable (drawer) desde la derecha con herramientas de
    inspección profunda, zoom, desglose de componentes, editor en vivo y exportación.
    """
    clean_code = sanitize_mermaid_code(diagram_code)
    parsed = parse_mermaid_elements(clean_code)

    st.caption(
        f"**{title}** • {parsed['total_nodes']} Componentes detectados • "
        f"{parsed['total_connections']} Relaciones • {parsed['total_subgraphs']} Dominios"
    )

    tab_view, tab_components, tab_editor, tab_export = st.tabs([
        "🔍 Vista Ampliada & Zoom",
        "🧩 Componentes y Flujos",
        "✏️ Editor en Vivo (Sandbox)",
        "💾 Exportar & Compartir",
    ])

    # ----------------------------------------------------
    # TAB 1: Vista Ampliada & Zoom
    # ----------------------------------------------------
    with tab_view:
        col_ctrl1, col_ctrl2 = st.columns([0.6, 0.4])
        with col_ctrl1:
            zoom_level = st.select_slider(
                "Nivel de Zoom / Escala",
                options=["75%", "100%", "125%", "150%", "200%"],
                value="100%",
                key="drawer_zoom_slider"
            )
        with col_ctrl2:
            st.write("")
            st.write("")
            if st.button("🖥️ Abrir en Modo Lienzo Completo", key="drawer_btn_fullscreen", use_container_width=True):
                st.session_state["fullscreen_diagram"] = clean_code
                st.session_state["fullscreen_title"] = title
                st.rerun()

        # Factor de escala
        zoom_map = {"75%": 0.75, "100%": 1.0, "125%": 1.25, "150%": 1.5, "200%": 2.0}
        scale_val = zoom_map.get(zoom_level, 1.0)

        st.markdown(
            f"""
            <div style="transform: scale({scale_val}); transform-origin: top center; transition: transform 0.2s ease;">
            """,
            unsafe_allow_html=True
        )
        st.mermaid_chart(clean_code, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 2: Desglose de componentes y flujos
    # ----------------------------------------------------
    with tab_components:
        st.markdown("#### 🧩 Catálogo de Elementos Arquitectónicos")
        if parsed["nodes"]:
            df_nodes = pd.DataFrame([
                {
                    "Icono": n["icon"],
                    "ID": n["id"],
                    "Nombre / Etiqueta": n["label"],
                    "Clasificación": n["type"]
                }
                for n in parsed["nodes"]
            ])
            _render_dataframe(df_nodes)
        else:
            st.info("No se identificaron nodos etiquetados individualmente.")

        if parsed["connections"]:
            st.markdown("#### 🔄 Relaciones e Interacciones Técnicas")
            df_conns = pd.DataFrame([
                {
                    "Origen": c["from"],
                    "Interacción / Protocolo": c["label"],
                    "Destino": c["to"]
                }
                for c in parsed["connections"]
            ])
            _render_dataframe(df_conns)

        if parsed["subgraphs"]:
            st.markdown("#### 🏛️ Dominios / Subgrafos")
            for sg in parsed["subgraphs"]:
                st.markdown(f"- 📦 **{sg}**")

    # ----------------------------------------------------
    # TAB 3: Editor interactivo
    # ----------------------------------------------------
    with tab_editor:
        st.markdown("#### ✏️ Modificar o Experimentar con el Diagrama")
        st.caption("Edita el código Mermaid para probar variaciones en tiempo real.")

        edited_code = st.text_area(
            "Código Mermaid",
            value=clean_code,
            height=280,
            key="drawer_editor_code"
        )

        if st.button("🔄 Actualizar Vista Previa", key="drawer_editor_refresh"):
            st.session_state["drawer_edited_code"] = edited_code

        current_preview = st.session_state.get("drawer_edited_code", edited_code)
        st.markdown("##### Vista Previa Actualizada:")
        try:
            st.mermaid_chart(sanitize_mermaid_code(current_preview), width="stretch")
        except Exception as e:
            st.error(f"Error en la sintaxis Mermaid: {str(e)}")

    # ----------------------------------------------------
    # TAB 4: Exportar y compartir
    # ----------------------------------------------------
    with tab_export:
        st.markdown("#### 💾 Exportar Diagrama")
        st.download_button(
            label="📥 Descargar Archivo Mermaid (.mmd)",
            data=clean_code,
            file_name="arquitectura_diagrama.mmd",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown("##### Código Fuente para Copiar:")
        st.code(clean_code, language="mermaid")


def render_diagram_card(diagram_code: str, unique_key: str, title: str = "Diagrama Conceptual de Arquitectura"):
    """
    Renderiza una tarjeta dinámica dentro del flujo de mensajes del chat con el diagrama
    insertado y un botón para deslizar hacia la vista detallada de inspección.
    """
    clean_code = sanitize_mermaid_code(diagram_code)
    parsed = parse_mermaid_elements(clean_code)

    # Cabecera dinámica de la tarjeta
    st.markdown(
        f"""
        <div class="arch-card-header">
            <div class="arch-card-title">
                <span>📐</span>
                <span>{title}</span>
            </div>
            <div class="arch-badge-live">
                ✨ {parsed['total_nodes']} Componentes • Clic para Deslizar
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Contenedor del diagrama
    with st.container(border=True):
        col_actions1, col_actions2, col_actions3 = st.columns([0.55, 0.25, 0.20])

        with col_actions1:
            st.caption("🔍 Haz clic en el botón para deslizar el panel de inspección profunda.")

        with col_actions2:
            if st.button("🔍 Ver a Detalle (Slide)", key=f"btn_drawer_{unique_key}", use_container_width=True, type="primary"):
                open_diagram_drawer(clean_code, title)

        with col_actions3:
            if st.button("🖥️ Modo Lienzo", key=f"btn_canvas_{unique_key}", use_container_width=True):
                st.session_state["fullscreen_diagram"] = clean_code
                st.session_state["fullscreen_title"] = title
                st.rerun()

        # Renderizar diagrama con Streamlit native mermaid_chart
        st.mermaid_chart(clean_code, width="stretch")


def render_message_with_diagrams(message: dict, message_index: int):
    """
    Renderiza un mensaje individual. Si contiene diagramas Mermaid, los extrae e
    inserta dinámicamente como tarjetas interactivas dentro del flujo del texto.
    """
    content = message.get("content", "")
    role = message.get("role", "assistant")

    with st.chat_message(role):
        # Para mensajes del usuario o mensajes sin mermaid, render normal
        if role != "assistant" or "```mermaid" not in content.lower():
            st.markdown(content)
            return

        segments = split_content_and_diagrams(content)

        diagram_counter = 0
        for seg in segments:
            if seg["type"] == "text":
                if seg["content"].strip():
                    st.markdown(seg["content"])
            elif seg["type"] == "diagram":
                diagram_counter += 1
                unique_key = f"msg_{message_index}_diag_{diagram_counter}"
                render_diagram_card(
                    diagram_code=seg["code"],
                    unique_key=unique_key,
                    title="Diagrama Conceptual de Arquitectura"
                )


def render_diagram_canvas_view():
    """
    Vista completa tipo Studio / Lienzo donde el usuario puede examinar el diagrama
    en pantalla completa con navegación, zoom y panel de herramientas.
    """
    diagram_code = st.session_state.get("fullscreen_diagram", "")
    diagram_title = st.session_state.get("fullscreen_title", "Diagrama Conceptual de Arquitectura")

    clean_code = sanitize_mermaid_code(diagram_code)
    parsed = parse_mermaid_elements(clean_code)

    st.markdown(
        f"""
        <div class="studio-banner">
            <div>
                <h2 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                    📐 Estudio de Arquitectura: {diagram_title}
                </h2>
                <span style="color: #94a3b8; font-size: 0.9rem;">
                    Vista detallada en pantalla completa • {parsed['total_nodes']} Nodos • {parsed['total_connections']} Relaciones
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Barra superior de navegación y controles
    top_col1, top_col2, top_col3 = st.columns([0.3, 0.4, 0.3])

    with top_col1:
        if st.button("⬅️ Volver a la Conversación", key="canvas_back_btn", type="primary", use_container_width=True):
            st.session_state["fullscreen_diagram"] = None
            st.rerun()

    with top_col2:
        zoom_level = st.select_slider(
            "Nivel de Zoom",
            options=["50%", "75%", "100%", "125%", "150%", "200%"],
            value="100%",
            key="canvas_zoom_slider"
        )

    with top_col3:
        st.download_button(
            label="📥 Descargar (.mmd)",
            data=clean_code,
            file_name="arquitectura_completa.mmd",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")

    zoom_map = {"50%": 0.5, "75%": 0.75, "100%": 1.0, "125%": 1.25, "150%": 1.5, "200%": 2.0}
    scale_val = zoom_map.get(zoom_level, 1.0)

    col_canvas, col_inspector = st.columns([0.7, 0.3])

    with col_canvas:
        st.markdown(
            f"""
            <div style="transform: scale({scale_val}); transform-origin: top left; transition: transform 0.25s ease;">
            """,
            unsafe_allow_html=True
        )
        st.mermaid_chart(clean_code, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_inspector:
        st.markdown("### 🧩 Inspector de Arquitectura")

        with st.expander("📦 Componentes y Actores", expanded=True):
            if parsed["nodes"]:
                df_nodes = pd.DataFrame([
                    {"Tipo": n["type"], "ID": n["id"], "Etiqueta": n["label"]}
                    for n in parsed["nodes"]
                ])
                _render_dataframe(df_nodes)
            else:
                st.info("Sin nodos detectados.")

        with st.expander("🔄 Conexiones y Flujos", expanded=True):
            if parsed["connections"]:
                df_conns = pd.DataFrame([
                    {"Desde": c["from"], "Interacción": c["label"], "Hacia": c["to"]}
                    for c in parsed["connections"]
                ])
                _render_dataframe(df_conns)

        with st.expander("💻 Código Fuente Mermaid"):
            st.code(clean_code, language="mermaid")
