"""
Parser y utilidades para diagramas Mermaid en respuestas del Architecture Agent.
"""
import re
from typing import Dict, List, Any


def sanitize_mermaid_code(code: str) -> str:
    """
    Limpia y normaliza el código Mermaid para asegurar que sea sintácticamente válido.
    Entrecomilla automáticamente etiquetas que contienen caracteres especiales o paréntesis
    para prevenir errores de sintaxis en el motor de renderizado de Mermaid.
    """
    if not code:
        return ""

    cleaned = code.strip()
    # Eliminar bloques de código markdown si están presentes
    cleaned = re.sub(r"^```(?:mermaid)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # Si no tiene un encabezado de diagrama Mermaid conocido, agregar 'flowchart TD' por defecto
    valid_headers = (
        "graph", "flowchart", "sequenceDiagram", "classDiagram",
        "stateDiagram", "erDiagram", "gantt", "pie", "gitGraph", "C4Context"
    )
    first_line = cleaned.split("\n", 1)[0].strip() if cleaned else ""
    if not any(first_line.startswith(h) for h in valid_headers):
        cleaned = f"flowchart TD\n{cleaned}"

    lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith("%%")
            or stripped.startswith("graph")
            or stripped.startswith("flowchart")
            or stripped.startswith("subgraph")
            or stripped.startswith("end")
        ):
            lines.append(line)
            continue

        # 1. Cilindros de Base de Datos: Node[(label)] -> Node[("label")]
        def fix_cylinder(match):
            node_id = match.group(1)
            content = match.group(2).strip()
            if content.startswith('"') and content.endswith('"'):
                return match.group(0)
            safe = content.replace('"', "'")
            return f'{node_id}[("{safe}")]'

        line = re.sub(r'([A-Za-z0-9_]+)\[\((.*?)\)\]', fix_cylinder, line)

        # 2. Rectángulos: Node[label] -> Node["label"]
        def fix_rect(match):
            node_id = match.group(1)
            content = match.group(2).strip()
            if (content.startswith('"') and content.endswith('"')) or content.startswith('('):
                return match.group(0)
            safe = content.replace('"', "'")
            return f'{node_id}["{safe}"]'

        line = re.sub(r'([A-Za-z0-9_]+)\[(?!\()([^\]\n]+)\]', fix_rect, line)

        # 3. Nodos redondeados: Node(label) -> Node("label")
        def fix_rounded(match):
            node_id = match.group(1)
            content = match.group(2).strip()
            if content.startswith('"') and content.endswith('"'):
                return match.group(0)
            safe = content.replace('"', "'")
            return f'{node_id}("{safe}")'

        line = re.sub(r'([A-Za-z0-9_]+)\((?!\()([^\)\n]+)\)', fix_rounded, line)

        # 4. Rombos de decisión: Node{label} -> Node{"label"}
        def fix_rhombus(match):
            node_id = match.group(1)
            content = match.group(2).strip()
            if content.startswith('"') and content.endswith('"'):
                return match.group(0)
            safe = content.replace('"', "'")
            return f'{node_id}{{"{safe}"}}'

        line = re.sub(r'([A-Za-z0-9_]+)\{([^\}\n]+)\}', fix_rhombus, line)

        lines.append(line)

    return "\n".join(lines)


def extract_mermaid_blocks(content: str) -> List[str]:
    """
    Extrae todos los bloques de código Mermaid presentes en un texto markdown.
    """
    if not content:
        return []
    pattern = re.compile(r"```mermaid\s*\n([\s\S]*?)```", re.IGNORECASE)
    matches = pattern.findall(content)
    return [sanitize_mermaid_code(m) for m in matches if m.strip()]


def split_content_and_diagrams(content: str) -> List[Dict[str, Any]]:
    """
    Divide el contenido markdown en fragmentos secuenciales de texto y diagramas Mermaid.
    Permite renderizar el texto previo, luego la tarjeta interactiva del diagrama, y después el texto restante.
    """
    if not content:
        return []

    pattern = re.compile(r"```mermaid\s*\n([\s\S]*?)```", re.IGNORECASE)
    segments: List[Dict[str, Any]] = []
    last_end = 0
    diagram_count = 0

    for match in pattern.finditer(content):
        start, end = match.span()
        # Texto previo al diagrama
        if start > last_end:
            text_part = content[last_end:start].strip()
            if text_part:
                segments.append({
                    "type": "text",
                    "content": text_part
                })
        
        # Diagrama Mermaid
        diagram_code = sanitize_mermaid_code(match.group(1))
        if diagram_code:
            diagram_count += 1
            segments.append({
                "type": "diagram",
                "code": diagram_code,
                "id": f"diagram_{diagram_count}",
                "raw": match.group(0),
                "index": diagram_count
            })
        last_end = end

    # Texto restante posterior al último diagrama
    if last_end < len(content):
        remaining_text = content[last_end:].strip()
        if remaining_text:
            segments.append({
                "type": "text",
                "content": remaining_text
            })

    # Si no se encontró ningún bloque de mermaid con ```mermaid, verificar si todo el texto es un diagrama
    if not segments and content.strip():
        segments.append({
            "type": "text",
            "content": content
        })

    return segments


def parse_mermaid_elements(code: str) -> Dict[str, Any]:
    """
    Analiza sintácticamente el código Mermaid para extraer componentes, actores,
    bases de datos, conexiones y estadísticas de arquitectura.
    """
    sanitized = sanitize_mermaid_code(code)
    lines = sanitized.splitlines()

    nodes: Dict[str, Dict[str, str]] = {}
    connections: List[Dict[str, str]] = []
    subgraphs: List[str] = []

    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("%%"):
            continue

        # Subgrafos / Dominios
        subgraph_match = re.match(r"^subgraph\s+([A-Za-z0-9_]+)?\s*\[?\"?([^\"\]]+)?\"?\]?", line_clean)
        if subgraph_match:
            title = subgraph_match.group(2) or subgraph_match.group(1) or "Subgrafo"
            subgraphs.append(title.strip())
            continue

        # Detectar bases de datos: ID[(Etiqueta)] o ID[("Etiqueta")]
        db_matches = re.findall(r"([A-Za-z0-9_]+)\s*\[\((.*?)\)\]", line_clean)
        for nid, nlbl in db_matches:
            clean_lbl = nlbl.strip().strip('"\'')
            nodes[nid] = {
                "id": nid,
                "label": clean_lbl,
                "type": "Base de Datos / Persistencia",
                "icon": "🗄️"
            }

        # Detectar nodos rectangulares (servicios, actores, APIs, etc.): ID[Etiqueta] o ID["Etiqueta"]
        rect_matches = re.findall(r"([A-Za-z0-9_]+)\s*\[(?!\()([^\]\n]+)\]", line_clean)
        for nid, nlbl in rect_matches:
            if nid not in nodes:
                clean_lbl = nlbl.strip().strip('"\'')
                lbl_lower = clean_lbl.lower()
                if any(k in lbl_lower for k in ("actor", "empleado", "usuario", "cliente", "admin", "user")):
                    ntype = "Actor / Usuario"
                    icon = "👤"
                elif any(k in lbl_lower for k in ("api", "extern", "proveedor", "third-party", "gateway", "service")):
                    ntype = "API / Integración Externa"
                    icon = "🌐"
                elif any(k in lbl_lower for k in ("cola", "queue", "kafka", "rabbit", "evento", "notif")):
                    ntype = "Mensajería / Eventos"
                    icon = "📬"
                else:
                    ntype = "Componente / Servicio"
                    icon = "⚙️"

                nodes[nid] = {
                    "id": nid,
                    "label": clean_lbl,
                    "type": ntype,
                    "icon": icon
                }

        # Detectar conexiones: A -->|Etiqueta| B, A <--|Etiqueta| B, A --> B, etc.
        conn_matches = re.findall(
            r'([A-Za-z0-9_]+)(?:\[.*?\]|\(.*?\))?\s*(?:<[-.=]+|[-.=]+>|[-.=]+)\s*(?:\|(.*?)\|)?\s*([A-Za-z0-9_]+)',
            line_clean
        )
        for src, lbl, dest in conn_matches:
            if src and dest:
                connections.append({
                    "from": src,
                    "to": dest,
                    "label": lbl.strip() if lbl else "interactúa con"
                })

    return {
        "nodes": list(nodes.values()),
        "connections": connections,
        "subgraphs": subgraphs,
        "total_nodes": len(nodes),
        "total_connections": len(connections),
        "total_subgraphs": len(subgraphs)
    }
