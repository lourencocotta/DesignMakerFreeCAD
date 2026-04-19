"""
Macro FreeCAD: Adicionar Parede

Adiciona uma parede entre dois pontos usando o módulo Arch.
Execute dentro do FreeCAD: Macro → Executar Macro → add_wall.py
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
START_X = 0.0   # metros
START_Y = 0.0   # metros
END_X = 5.0     # metros
END_Y = 0.0     # metros
THICKNESS = 0.15  # metros
HEIGHT = 2.80     # metros
MATERIAL = "alvenaria"
WALL_LABEL = "Parede_01"
# ──────────────────────────────────────────────────────────────────────────────

MATERIAL_COLORS = {
    "alvenaria": (0.8, 0.7, 0.6),
    "drywall": (0.95, 0.95, 0.95),
    "concreto": (0.5, 0.5, 0.5),
}


def mm(v: float) -> float:
    return v * 1000


def add_wall(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    thickness: float = 0.15,
    height: float = 2.80,
    material: str = "alvenaria",
    label: str = "Parede",
) -> object:
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    line = Draft.makeLine(
        FreeCAD.Vector(mm(start_x), mm(start_y), 0),
        FreeCAD.Vector(mm(end_x), mm(end_y), 0),
    )
    line.Label = f"{label}_Eixo"
    line.ViewObject.Visibility = False

    wall = Arch.makeWall(line, length=None, width=mm(thickness), height=mm(height))
    wall.Label = label

    color = MATERIAL_COLORS.get(material, (0.8, 0.7, 0.6))
    wall.ViewObject.ShapeColor = color

    import math
    length = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
    FreeCAD.Console.PrintMessage(
        f"Parede '{label}': {length:.2f}m × {thickness}m × {height}m "
        f"[{material}]\n"
    )

    doc.recompute()
    return wall


if __name__ == "__main__":
    add_wall(
        START_X, START_Y, END_X, END_Y, THICKNESS, HEIGHT, MATERIAL, WALL_LABEL
    )
