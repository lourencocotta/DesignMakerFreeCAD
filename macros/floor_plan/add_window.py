"""
Macro FreeCAD: Adicionar Janela

Insere uma janela em uma parede existente no documento ativo.
Execute dentro do FreeCAD: Macro → Executar Macro → add_window.py
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
WALL_LABEL = "Parede_01"
POSITION_X = 1.20      # metros a partir do início da parede
WIDTH = 1.20            # metros
HEIGHT = 1.20           # metros
SILL_HEIGHT = 0.90      # peitoril em metros (NBR: mín. 0.90m para segurança)
WINDOW_TYPE = "correr"  # maxim-ar | correr | guilhotina | basculante | fixa
WINDOW_LABEL = "Janela_01"
# ──────────────────────────────────────────────────────────────────────────────

WINDOW_PRESETS = {
    "correr": "Sliding door",
    "maxim-ar": "Open 2-pane",
    "guilhotina": "Sash window 2-pane",
    "basculante": "Open 1-pane",
    "fixa": "Fixed",
}


def mm(v: float) -> float:
    return v * 1000


def illumination_check(room_area: float, window_area: float) -> dict:
    """NBR 15575: iluminação mínima = 1/8 da área do piso."""
    min_required = room_area / 8
    return {
        "window_area_m2": round(window_area, 3),
        "min_required_m2": round(min_required, 3),
        "compliant": window_area >= min_required,
    }


def add_window(
    wall_label: str,
    position_x: float,
    width: float = 1.20,
    height: float = 1.20,
    sill_height: float = 0.90,
    window_type: str = "correr",
    label: str = "Janela",
) -> object:
    doc = FreeCAD.ActiveDocument
    if not doc:
        FreeCAD.Console.PrintError("Nenhum documento ativo.\n")
        return None

    wall = None
    for obj in doc.Objects:
        if obj.Label == wall_label and hasattr(obj, "Width"):
            wall = obj
            break

    if wall is None:
        FreeCAD.Console.PrintError(f"Parede '{wall_label}' não encontrada.\n")
        return None

    preset_name = WINDOW_PRESETS.get(window_type, "Sliding door")

    window = Arch.makeWindowPreset(
        preset_name,
        width=mm(width),
        height=mm(height),
        h1=mm(0.05),
        h2=mm(0.05),
        h3=mm(0.05),
        w1=mm(0.05),
        w2=mm(0.05),
        o1=0,
        o2=mm(0.05),
        placement=FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill_height)),
            FreeCAD.Rotation(),
        ),
    )
    window.Label = label
    window.Hosts = [wall]

    if sill_height < 0.90:
        FreeCAD.Console.PrintWarning(
            f"ATENÇÃO: Peitoril '{label}' ({sill_height}m) abaixo do recomendado "
            f"pela NBR 9050 (0.90m)!\n"
        )

    FreeCAD.Console.PrintMessage(
        f"Janela '{label}': {width}m × {height}m [{window_type}] "
        f"peitoril={sill_height}m | Área={width*height:.3f}m²\n"
    )
    doc.recompute()
    return window


if __name__ == "__main__":
    add_window(
        WALL_LABEL, POSITION_X, WIDTH, HEIGHT, SILL_HEIGHT, WINDOW_TYPE, WINDOW_LABEL
    )
