"""Generate diagrams.net (.drawio) mxGraphModel XML files."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


@dataclass
class DrawioNode:
    id: str
    label: str
    x: float = 40.0
    y: float = 40.0
    width: float = 120.0
    height: float = 60.0
    style: str = "rounded=1;whiteSpace=wrap;html=1;"


@dataclass
class DrawioEdge:
    id: str
    source: str
    target: str
    label: str = ""


@dataclass
class DrawioDiagram:
    name: str = "Page-1"
    nodes: list[DrawioNode] = field(default_factory=list)
    edges: list[DrawioEdge] = field(default_factory=list)


def _new_id(prefix: str = "") -> str:
    return prefix + uuid.uuid4().hex[:12]


def from_json(data: dict[str, Any]) -> DrawioDiagram:
    """Parse JSON {nodes: [...], edges: [...]} into DrawioDiagram."""
    diagram = DrawioDiagram(name=data.get("name", "Page-1"))
    x, y = 40.0, 40.0
    id_map: dict[str, str] = {}

    for raw in data.get("nodes", []):
        node_id = raw.get("id") or _new_id("n")
        id_map[raw.get("key", node_id)] = node_id
        diagram.nodes.append(
            DrawioNode(
                id=node_id,
                label=str(raw.get("label", node_id)),
                x=float(raw.get("x", x)),
                y=float(raw.get("y", y)),
                width=float(raw.get("width", 120)),
                height=float(raw.get("height", 60)),
                style=str(raw.get("style", "rounded=1;whiteSpace=wrap;html=1;")),
            )
        )
        y += 100

    for raw in data.get("edges", []):
        src_key = raw.get("source", "")
        tgt_key = raw.get("target", "")
        src = id_map.get(src_key, src_key)
        tgt = id_map.get(tgt_key, tgt_key)
        diagram.edges.append(
            DrawioEdge(
                id=raw.get("id") or _new_id("e"),
                source=src,
                target=tgt,
                label=str(raw.get("label", "")),
            )
        )
    return diagram


def from_mermaid(text: str) -> DrawioDiagram:
    """
    Minimal mermaid flowchart parser (flowchart TD / graph TD).
    Supports: A[Label] --> B[Label]
    """
    import re

    diagram = DrawioDiagram()
    node_labels: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []

    def node_id(token: str) -> str:
        match = re.match(r"(\w+)", token.strip())
        return match.group(1) if match else token.strip()

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("%%"):
            continue
        if line.lower().startswith(("flowchart", "graph")):
            continue

        for match in re.finditer(r"(\w+)\s*[\[\(]([^\]\)]+)[\]\)]", line):
            node_labels[match.group(1)] = match.group(2)

        if "-->" in line:
            parts = line.split("-->", 1)
            if len(parts) == 2:
                src = node_id(parts[0])
                tgt = node_id(parts[1])
                label = ""
                lbl_match = re.search(r"\|([^|]+)\|", line)
                if lbl_match:
                    label = lbl_match.group(1)
                edges.append((src, tgt, label))
                for key in (src, tgt):
                    if key and key not in node_labels:
                        node_labels[key] = key

    x, y = 40.0, 40.0
    id_map: dict[str, str] = {}
    for key, label in node_labels.items():
        nid = _new_id("n")
        id_map[key] = nid
        diagram.nodes.append(DrawioNode(id=nid, label=label, x=x, y=y))
        x += 160
        if x > 800:
            x = 40
            y += 120

    for src_key, tgt_key, label in edges:
        diagram.edges.append(
            DrawioEdge(
                id=_new_id("e"),
                source=id_map.get(src_key, src_key),
                target=id_map.get(tgt_key, tgt_key),
                label=label,
            )
        )
    return diagram


def to_drawio_xml(diagram: DrawioDiagram) -> str:
    """Serialize diagram to .drawio file content."""
    mxfile = ET.Element(
        "mxfile",
        host="app.diagrams.net",
        agent="Workflow-document-conversion",
        version="24.0.0",
    )
    diagram_el = ET.SubElement(
        mxfile,
        "diagram",
        name=diagram.name,
        id=_new_id("d"),
    )

    model = ET.Element(
        "mxGraphModel",
        dx="1200",
        dy="800",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth="827",
        pageHeight="1169",
        math="0",
        shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for node in diagram.nodes:
        cell = ET.SubElement(
            root,
            "mxCell",
            id=node.id,
            value=_escape_xml(node.label),
            style=node.style,
            vertex="1",
            parent="1",
        )
        geo = ET.SubElement(cell, "mxGeometry", x=str(node.x), y=str(node.y))
        geo.set("width", str(node.width))
        geo.set("height", str(node.height))
        geo.set("as", "geometry")

    for edge in diagram.edges:
        style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        cell = ET.SubElement(
            root,
            "mxCell",
            id=edge.id,
            value=_escape_xml(edge.label),
            style=style,
            edge="1",
            parent="1",
            source=edge.source,
            target=edge.target,
        )
        geo = ET.SubElement(cell, "mxGeometry", relative="1")
        geo.set("as", "geometry")

    diagram_el.append(model)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mxfile, encoding="unicode")


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_drawio(diagram: DrawioDiagram, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_drawio_xml(diagram), encoding="utf-8")
    return output_path


def load_input(input_path: Path) -> DrawioDiagram:
    """Load JSON or .mmd mermaid file."""
    input_path = Path(input_path)
    text = input_path.read_text(encoding="utf-8")
    suffix = input_path.suffix.lower()

    if suffix == ".json":
        return from_json(json.loads(text))
    if suffix in (".mmd", ".mermaid"):
        return from_mermaid(text)

    # Auto-detect
    text_stripped = text.strip()
    if text_stripped.startswith("{"):
        return from_json(json.loads(text))
    return from_mermaid(text)
