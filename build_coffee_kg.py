from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import pandas as pd
import networkx as nx
from pyvis.network import Network


def slugify(s: str) -> str:
    """
    Standardizes a string into a slug format suitable for IDs
    Returns lowercase alphanumeric and hyphens only
    """
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "unknown"


def parse_note_intensities(s: str) -> Dict[str, int]:
    """
    Parse strings like: "chocolate:4;fruit:3" for flavor notes and intensities
    Returns dict {"chocolate": 4, "fruit": 3}
    """
    out: Dict[str, int] = {}
    if not isinstance(s, str) or not s.strip():
        return out
    parts = [p.strip() for p in s.split(";") if p.strip()]
    for p in parts:
        if ":" not in p:
            continue
        note, intensity = p.split(":", 1)
        note = note.strip()
        try:
            intensity_i = int(intensity.strip())
        except ValueError:
            continue
        if note:
            out[note] = intensity_i
    return out


def ensure_node(
    G: nx.MultiDiGraph,
    node_id: str,
    label: str,
    node_type: str,
    **props,
) -> None:
    """
    This function ensures that a node with the given ID exists in the graph G.
    If the node does not exist, it creates it with the provided label, type, and properties.
    If the node already exists, it updates its properties with any new non-null values provided.
    """
    if node_id not in G:
        G.add_node(node_id, label=label, type=node_type, **props)
    else:
        # Merge/update properties (keep existing unless new non-null provided)
        for k, v in props.items():
            if v is not None and v != "" and (k not in G.nodes[node_id] or G.nodes[node_id][k] in (None, "")):
                G.nodes[node_id][k] = v


def add_edge(
    G: nx.MultiDiGraph,
    src: str,
    rel: str,
    dst: str,
    **props,
) -> None:
    """
    For adding an edge with relationship type and properties
    """
    G.add_edge(src, dst, key=rel, type=rel, **props)


def build_graph_from_brews(csv_path: str) -> nx.MultiDiGraph:
    """
    Builds a graph from a CSV file containing brew data.
    """
    df = pd.read_csv(csv_path)

    # Core columns are all non-method-specific parameters.
    # Any column NOT in this set will be treated as a dynamic, optional parameter.
    core_columns = {
        "brew_id", "barista", "brew_date", "roaster", "coffee_name", "roast_level", "roast_date",
        "brew_method", "brewer_brand", "brewer_model", "dose_g", "total_brew_time_sec",
        "notes_intensities", "sweetness_0_10", "acidity_0_10", "bitterness_0_10", "body_0_10",
        "overall_0_10", "grinder", "grind_setting", "filter_material", "notes_overall"
    }

    # Enforce required columns
    required = ["brew_id", "barista", "brew_date", "roaster", "coffee_name", "roast_level",
                "brew_method", "brewer_brand", "brewer_model", "dose_g", "total_brew_time_sec",
                "notes_intensities","sweetness_0_10","acidity_0_10","bitterness_0_10","body_0_10",
                "overall_0_10"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    G = nx.MultiDiGraph()

    for _, r in df.iterrows():
        # --- Data Cleaning and Preparation ---
        # Read all values from the row and clean them up first.
        brew_id = str(r.get("brew_id", "unknown"))
        barista = str(r.get("barista", "unknown"))
        brew_date = str(r.get("brew_date", "unknown"))
        dose_g = float(r.get("dose_g", 0.0))
        total_brew_time_sec=float(r.get("total_brew_time_sec",0.0))
        
        roaster = str(r.get("roaster", "unknown"))
        coffee_name = str(r.get("coffee_name", "unknown"))
        roast_date = str(r.get("roast_date", "")) if pd.notna(r.get("roast_date", None)) else ""
        roast_level = str(r.get("roast_level", "unknown"))

        grinder = str(r.get("grinder", "unknown"))
        grind_setting = str(r.get("grind_setting", "unknown"))

        brew_method = str(r.get("brew_method", "unknown"))
        brewer_brand = str(r.get("brewer_brand", "unknown"))
        brewer_model = str(r.get("brewer_model", "unknown"))
        filter_material = str(r.get("filter_material", "")) if pd.notna(r.get("filter_material", None)) else ""

        notes_overall=str(r.get("notes_overall", "")) if pd.notna(r.get("notes_overall", None)) else ""
        sweetness_0_10=float(r.get("sweetness_0_10",0.0))
        acidity_0_10=float(r.get("acidity_0_10",0.0))
        bitterness_0_10=float(r.get("bitterness_0_10",0.0))
        body_0_10=float(r.get("body_0_10",0.0))
        overall_0_10=float(r.get("overall_0_10",0.0))

        note_map = parse_note_intensities(str(r.get("notes_intensities", "")))

        # --- Node ID Generation ---
        # Create stable-ish node IDs for reusable entities
        roaster_id = f"roaster:{slugify(roaster)}"
        beanlot_id = f"bean:{slugify(roaster)}:{slugify(coffee_name)}"
        roastbatch_id = f"roast:{slugify(roaster)}:{slugify(coffee_name)}:{slugify(roast_level)}"
        grinder_id = f"grinder:{slugify(grinder)}"
        brewer_id = f"brewer:{slugify(brewer_brand)}-{slugify(brewer_model)}"
        
        brew_session_id = f"brew:{slugify(brew_id)}"
        eval_id = f"eval:{slugify(brew_id)}"

        # --- Graph Building: Nodes ---
        ensure_node(G, roaster_id, label=roaster, node_type="Roaster")
        ensure_node(G, beanlot_id, label=coffee_name, node_type="BeanLot")
        ensure_node(G, roastbatch_id, label=f"{coffee_name} ({roast_level})", node_type="RoastBatch", roast_level=roast_level)
        ensure_node(G, grinder_id, label=grinder, node_type="Grinder")
        ensure_node(G, brewer_id, label=f"{brewer_brand} {brewer_model}".strip(),
                    node_type="Brewer", brand=brewer_brand, model=brewer_model, filter_material=filter_material)

        ensure_node(
            G,
            brew_session_id,
            label=brew_id,
            node_type="BrewSession",
            dose_g=dose_g,
            total_brew_time_sec=total_brew_time_sec,
            notes_overall=notes_overall,
            barista=barista,
            brew_date=brew_date
        )

        ensure_node(
            G,
            eval_id,
            label=f"Eval {brew_id}",
            node_type="SensoryEvaluation",
            sweetness_0_10=sweetness_0_10,
            acidity_0_10=acidity_0_10,
            bitterness_0_10=bitterness_0_10,
            body_0_10=body_0_10,
            overall_0_10=overall_0_10
        )

        for note, intensity in note_map.items():
            note_id = f"note:{slugify(note)}"
            ensure_node(G, note_id, label=note, node_type="FlavorNote")

        # --- Graph Building: Edges ---
        # Dynamically find and store all other optional parameters on the BREWED_WITH edge
        method_params = {'brew_method': brew_method}
        for col_name in df.columns:
            if col_name not in core_columns:
                value = r.get(col_name)
                if pd.notna(value) and value != "":
                    # Try to convert to float if possible, otherwise keep as string
                    try:
                        method_params[col_name] = float(value)
                    except (ValueError, TypeError):
                        method_params[col_name] = str(value)
        
        add_edge(G, roaster_id, "PRODUCES", beanlot_id)
        add_edge(G, beanlot_id, "ROASTED_AS", roastbatch_id, roast_date=roast_date)
        add_edge(G, brew_session_id, "USES_GRINDER", grinder_id, grind_setting=grind_setting)
        add_edge(G, brew_session_id, "BREWED_WITH", brewer_id, **method_params)
        add_edge(G, brew_session_id, "USES_ROAST", roastbatch_id)
        add_edge(G, brew_session_id, "EVALUATED_AS", eval_id)

        # Flavor notes as nodes + intensity on edges
        for note, intensity in note_map.items():
            note_id = f"note:{slugify(note)}"
            add_edge(G, eval_id, "HAS_NOTE", note_id, intensity=intensity)

    return G


def export_pyvis_html(G: nx.MultiDiGraph, out_html: str = "coffee_kg.html") -> None:
    net = Network(height="800px", width="100%", directed=True, notebook=False)

    # Basic styling by node type
    type_to_color = {
        "Roaster": "#b22222",
        "BeanLot": "#2e8b57",
        "RoastBatch": "#8b4513",
        "Grinder": "#4682b4",
        "GrindSetting": "#4169e1",
        "Brewer": "#6a5acd",
        "BrewSession": "#111111",
        "SensoryEvaluation": "gold",
        "FlavorNote": "#ff8c00"
    }

    for nid, attrs in G.nodes(data=True):
        ntype = attrs.get("type", "Thing")
        label = attrs.get("label", nid)

        # Put extra info in hover tooltip
        hover = "\n".join([f"{k}: {v}" for k, v in attrs.items() if k not in ("label",)])

        net.add_node(
            nid,
            label=label,
            title=hover,
            color=type_to_color.get(ntype, "#cccccc"),
        )

    for u, v, k, attrs in G.edges(keys=True, data=True):
        rel = attrs.get("type", k)
        title = "\n".join([f"{k2}: {v2}" for k2, v2 in attrs.items()])
        net.add_edge(u, v, label=rel, title=title, arrows="to")

    net.toggle_physics(True)
    net.write_html(out_html, open_browser=False, notebook=False)
    print(f"Wrote {out_html}")


if __name__ == "__main__":
    G = build_graph_from_brews("brews.csv")
    export_pyvis_html(G, "coffee_kg.html")