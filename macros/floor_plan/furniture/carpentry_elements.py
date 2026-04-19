"""
Macro FreeCAD: Elementos de Carpintaria

Cria representações 2D/3D de móveis planejados e elementos de carpintaria.
Execute dentro do FreeCAD: Macro → Executar Macro → carpentry_elements.py
"""

import FreeCAD
import FreeCADGui
import Part
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
FURNITURE_TYPE = "armario_cozinha_alto"
POSITION_X = 0.0
POSITION_Y = 0.0
ROTATION_DEG = 0.0
MATERIAL = "MDF"
# ──────────────────────────────────────────────────────────────────────────────

# Catálogo de medidas padrão (metros)
FURNITURE_CATALOG = {
    "armario_cozinha_alto": {"w": 0.60, "d": 0.35, "h": 2.10, "color": (0.9, 0.8, 0.6)},
    "armario_cozinha_baixo": {"w": 0.60, "d": 0.55, "h": 0.85, "color": (0.9, 0.8, 0.6)},
    "bancada_cozinha": {"w": 0.60, "d": 0.60, "h": 0.90, "color": (0.8, 0.8, 0.8)},
    "guarda_roupa_casal": {"w": 2.00, "d": 0.60, "h": 2.10, "color": (0.85, 0.75, 0.6)},
    "guarda_roupa_solteiro": {"w": 1.20, "d": 0.50, "h": 2.10, "color": (0.85, 0.75, 0.6)},
    "cama_casal": {"w": 1.38, "d": 1.88, "h": 0.45, "color": (0.7, 0.85, 0.95)},
    "cama_queen": {"w": 1.58, "d": 1.98, "h": 0.45, "color": (0.7, 0.85, 0.95)},
    "cama_solteiro": {"w": 0.88, "d": 1.88, "h": 0.45, "color": (0.7, 0.85, 0.95)},
    "sofa_3_lugares": {"w": 2.10, "d": 0.85, "h": 0.85, "color": (0.6, 0.7, 0.8)},
    "mesa_jantar_4": {"w": 1.20, "d": 0.80, "h": 0.75, "color": (0.7, 0.55, 0.4)},
    "mesa_jantar_6": {"w": 1.60, "d": 0.90, "h": 0.75, "color": (0.7, 0.55, 0.4)},
    "vaso_sanitario": {"w": 0.37, "d": 0.65, "h": 0.80, "color": (0.95, 0.95, 0.95)},
    "pia_banheiro": {"w": 0.50, "d": 0.45, "h": 0.85, "color": (0.95, 0.95, 0.95)},
    "box_banheiro": {"w": 0.90, "d": 0.90, "h": 2.00, "color": (0.8, 0.9, 1.0)},
    "geladeira": {"w": 0.70, "d": 0.80, "h": 1.80, "color": (0.85, 0.85, 0.9)},
    "fogao_4_bocas": {"w": 0.56, "d": 0.56, "h": 0.85, "color": (0.3, 0.3, 0.3)},
}


def mm(v: float) -> float:
    return v * 1000


def add_furniture(
    furniture_type: str,
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    rotation_deg: float = 0.0,
    custom_w: float = None,
    custom_d: float = None,
    custom_h: float = None,
    label: str = None,
) -> object:
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    spec = FURNITURE_CATALOG.get(furniture_type)
    if not spec:
        FreeCAD.Console.PrintError(
            f"Tipo '{furniture_type}' não encontrado. "
            f"Disponíveis: {list(FURNITURE_CATALOG.keys())}\n"
        )
        return None

    w = mm(custom_w or spec["w"])
    d = mm(custom_d or spec["d"])
    h = mm(custom_h or spec["h"])

    box = doc.addObject("Part::Box", label or furniture_type)
    box.Length = w
    box.Width = d
    box.Height = h
    box.Label = label or furniture_type

    import math
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rotation_deg)
    box.Placement = FreeCAD.Placement(
        FreeCAD.Vector(mm(pos_x), mm(pos_y), 0), rot
    )

    color = spec.get("color", (0.8, 0.7, 0.6))
    box.ViewObject.ShapeColor = color

    FreeCAD.Console.PrintMessage(
        f"Móvel '{box.Label}': {spec['w']}m × {spec['d']}m × {spec['h']}m "
        f"em ({pos_x}, {pos_y})\n"
    )
    doc.recompute()
    return box


if __name__ == "__main__":
    add_furniture(FURNITURE_TYPE, POSITION_X, POSITION_Y, ROTATION_DEG)
