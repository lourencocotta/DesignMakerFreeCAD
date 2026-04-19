"""
Macro FreeCAD: Criar Cômodo

Cria um cômodo retangular com paredes de alvenaria usando o módulo Arch do FreeCAD.
Execute dentro do FreeCAD: Macro → Executar Macro → create_room.py

Parâmetros configuráveis abaixo.
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
ROOM_NAME = "Sala de Estar"
ORIGIN_X = 0.0    # metros
ORIGIN_Y = 0.0    # metros
WIDTH = 4.0       # metros
DEPTH = 3.5       # metros
WALL_THICKNESS = 0.15  # metros
WALL_HEIGHT = 2.80     # metros
# ──────────────────────────────────────────────────────────────────────────────


def mm(value: float) -> float:
    """Converte metros para milímetros (unidade interna do FreeCAD)."""
    return value * 1000


def create_room(
    name: str,
    origin_x: float,
    origin_y: float,
    width: float,
    depth: float,
    wall_thickness: float = 0.15,
    wall_height: float = 2.80,
):
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("PlantaBaixa")

    ox, oy = mm(origin_x), mm(origin_y)
    w, d = mm(width), mm(depth)
    t, h = mm(wall_thickness), mm(wall_height)

    # Eixos das 4 paredes (linha central)
    axes = [
        ([ox, oy, 0], [ox + w, oy, 0]),          # Sul
        ([ox + w, oy, 0], [ox + w, oy + d, 0]),  # Leste
        ([ox + w, oy + d, 0], [ox, oy + d, 0]),  # Norte
        ([ox, oy + d, 0], [ox, oy, 0]),           # Oeste
    ]
    directions = ["Sul", "Leste", "Norte", "Oeste"]

    walls = []
    for i, (start, end) in enumerate(axes):
        line = Draft.makeLine(
            FreeCAD.Vector(*start),
            FreeCAD.Vector(*end),
        )
        line.Label = f"{name}_Eixo_{directions[i]}"

        wall = Arch.makeWall(line, length=None, width=t, height=h)
        wall.Label = f"{name}_Parede_{directions[i]}"
        walls.append(wall)

    doc.recompute()
    FreeCAD.Console.PrintMessage(
        f"Cômodo '{name}' criado: {width}m × {depth}m | "
        f"Área: {width * depth:.2f}m²\n"
    )
    return walls


if __name__ == "__main__":
    create_room(
        ROOM_NAME, ORIGIN_X, ORIGIN_Y, WIDTH, DEPTH, WALL_THICKNESS, WALL_HEIGHT
    )
