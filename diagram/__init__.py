"""
Módulo de diagramas de arquitectura para el Architecture Agent.
"""
from diagram.parser import (
    sanitize_mermaid_code,
    extract_mermaid_blocks,
    split_content_and_diagrams,
    parse_mermaid_elements,
)
from diagram.viewer import (
    inject_diagram_styles,
    render_message_with_diagrams,
    open_diagram_drawer,
    render_diagram_canvas_view,
)

__all__ = [
    "sanitize_mermaid_code",
    "extract_mermaid_blocks",
    "split_content_and_diagrams",
    "parse_mermaid_elements",
    "inject_diagram_styles",
    "render_message_with_diagrams",
    "open_diagram_drawer",
    "render_diagram_canvas_view",
]
