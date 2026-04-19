"""
Macro FreeCAD: Adicionar Porta

Insere uma porta em uma parede existente no documento ativo.
Execute dentro do FreeCAD: Macro → Executar Macro → add_door.py
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
WALL_LABEL = "Parede_01"     # Label da parede alvo
POSITION_X = 1.0             # metros a partir do início da parede
WIDTH = 0.90                 # metros
HEIGHT = 2.10                # metros
SILL = 0.0                   # peitoril (0 para porta)
DOOR_TYPE = "simples"        # simples | dupla | correr | pivotante
OPENING_SIDE = "left"        # left | right
DOOR_LABEL = "Porta_01"
# ──────────────────────────────────────────────────────────────────────────────

# Dimensões padrão NBR — larguras mínimas
NBR_MINIMUMS = {
    "acesso_principal": 0.90,
    "quarto": 0.80,
    "banheiro": 0.70,
    "servico": 0.80,
    "garagem": 2.40,
}


def mm(v: float) -> float:
    return v * 1000


def add_door(
    wall_label: str,
    position_x: float,
    width: float = 0.90,
    height: float = 2.10,
    sill: float = 0.0,
    door_type: str = "simples",
    opening_side: str = "left",
    label: str = "Porta",
) -> object:
    doc = FreeCAD.ActiveDocument
    if not doc:
        FreeCAD.Console.PrintError("Nenhum documento ativo.\n")
        return None

    # Localiza a parede pelo label
    wall = None
    for obj in doc.Objects:
        if obj.Label == wall_label and hasattr(obj, "Width"):
            wall = obj
            break

    if wall is None:
        FreeCAD.Console.PrintError(f"Parede '{wall_label}' não encontrada.\n")
        return None

    # Cria uma janela/porta com preset do Arch
    door = Arch.makeWindowPreset(
        "Simple door",
        width=mm(width),
        height=mm(height),
        h1=mm(0.1),
        h2=mm(0.1),
        h3=mm(0.1),
        w1=mm(0.1),
        w2=mm(0.1),
        o1=0,
        o2=mm(0.1),
        placement=FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill)),
            FreeCAD.Rotation(),
        ),
    )
    door.Label = label
    door.Hosts = [wall]

    if width < 0.80:
        FreeCAD.Console.PrintWarning(
            f"ATENÇÃO: Porta '{label}' ({width}m) abaixo do mínimo NBR (0.80m)!\n"
        )

    FreeCAD.Console.PrintMessage(
        f"Porta '{label}': {width}m × {height}m [{door_type}] na parede '{wall_label}'\n"
    )
    doc.recompute()
    return door


if __name__ == "__main__":
    add_door(
        WALL_LABEL, POSITION_X, WIDTH, HEIGHT, SILL, DOOR_TYPE, OPENING_SIDE, DOOR_LABEL
    )
