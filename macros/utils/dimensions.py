"""
Macro FreeCAD: Utilitários de Cotas

Funções auxiliares para inserir dimensões, textos e títulos em plantas baixas.
"""

import FreeCAD
import Draft
import math


def add_linear_dimension(
    start: list,
    end: list,
    offset: float = 0.5,
    label: str = "Cota",
) -> object:
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    def mm(v):
        return v * 1000

    p1 = FreeCAD.Vector(mm(start[0]), mm(start[1]), 0)
    p2 = FreeCAD.Vector(mm(end[0]), mm(end[1]), 0)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx * dx + dy * dy)
    nx, ny = -dy / (length or 1), dx / (length or 1)

    mid_x = (start[0] + end[0]) / 2 + nx * offset
    mid_y = (start[1] + end[1]) / 2 + ny * offset
    p_mid = FreeCAD.Vector(mm(mid_x), mm(mid_y), 0)

    dim = Draft.makeDimension(p1, p2, p_mid)
    dim.Label = label
    dim.ViewObject.FontSize = 150  # 150mm = texto legível em escala 1:100
    dim.ViewObject.ArrowSize = 100
    dim.ViewObject.ArrowType = "Arrow"

    doc.recompute()
    FreeCAD.Console.PrintMessage(
        f"Cota '{label}': {length:.3f}m\n"
    )
    return dim


def add_room_label(
    position: list,
    name: str,
    area: float,
    font_size: float = 0.20,
) -> object:
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    def mm(v):
        return v * 1000

    text = Draft.makeText(
        [name, f"A={area:.2f}m²"],
        point=FreeCAD.Vector(mm(position[0]), mm(position[1]), 0),
    )
    text.Label = f"Label_{name}"
    text.ViewObject.FontSize = mm(font_size)

    doc.recompute()
    return text


def add_north_arrow(position: list, size: float = 0.5) -> None:
    """Adiciona símbolo de Norte (seta) na planta."""
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    def mm(v):
        return v * 1000

    x, y = position
    arrow = Draft.makeText(
        ["N"],
        point=FreeCAD.Vector(mm(x), mm(y + size), 0),
    )
    arrow.Label = "Norte"
    arrow.ViewObject.FontSize = mm(size * 0.6)

    line = Draft.makeLine(
        FreeCAD.Vector(mm(x), mm(y), 0),
        FreeCAD.Vector(mm(x), mm(y + size), 0),
    )
    line.Label = "Seta_Norte"

    doc.recompute()
