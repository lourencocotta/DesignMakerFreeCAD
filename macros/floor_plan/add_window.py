"""
Macro FreeCAD: Adicionar Janela

Insere uma janela em uma parede existente no documento ativo.
Execute dentro do FreeCAD: Macro → Executar Macro → add_window.py

COMO USAR:
  1. Execute create_room.py primeiro para criar as paredes.
  2. No Report View (Menu Ver → Painéis → Saída do relatório) anote o Label
     da parede onde quer inserir a janela (ex: "Sala de Estar_Parede_Norte").
  3. Cole esse Label em WALL_LABEL abaixo e execute esta macro.
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
# Coloque aqui o Label EXATO da parede (veja o Report View após create_room.py)
# Exemplos: "Sala de Estar_Parede_Norte" | "Quarto_Parede_Leste" | "Wall002"
WALL_LABEL = "Sala de Estar_Parede_Norte"
POSITION_X = 1.20      # metros a partir do início da parede
WIDTH = 1.20            # metros
HEIGHT = 1.20           # metros
SILL_HEIGHT = 0.90      # peitoril em metros (NBR: mín. 0.90m para segurança)
WINDOW_TYPE = "correr"  # maxim-ar | correr | guilhotina | basculante | fixa
WINDOW_LABEL = "Janela_01"
# ──────────────────────────────────────────────────────────────────────────────

def mm(v: float) -> float:
    return v * 1000


def _find_wall(doc, identifier: str):
    """Busca parede por Label exato, Name exato ou Label parcial (case-insensitive)."""
    walls = [o for o in doc.Objects if hasattr(o, "Width") and hasattr(o, "Height")]

    for w in walls:
        if w.Label == identifier:
            return w
    for w in walls:
        if w.Name == identifier:
            return w
    identifier_lower = identifier.lower()
    for w in walls:
        if identifier_lower in w.Label.lower():
            return w
    return None


def _list_walls(doc) -> None:
    walls = [o for o in doc.Objects if hasattr(o, "Width") and hasattr(o, "Height")]
    if not walls:
        FreeCAD.Console.PrintError("Nenhuma parede encontrada no documento.\n")
        return
    FreeCAD.Console.PrintMessage("Paredes disponíveis no documento:\n")
    for w in walls:
        FreeCAD.Console.PrintMessage(f"  Name={w.Name!r:12s}  Label={w.Label!r}\n")


WINDOW_PRESETS = {
    "correr": "Open 2-pane",
    "maxim-ar": "Open 2-pane",
    "guilhotina": "Sash window 2-pane",
    "basculante": "Open 1-pane",
    "fixa": "Fixed",
}

# Presets garantidos em todas as versões do FreeCAD Arch
_SAFE_PRESETS = {"Fixed", "Open 1-pane", "Open 2-pane",
                 "Sash window 2-pane", "Sash window 4-pane", "Simple door", "Glass door"}


def illumination_check(room_area: float, window_area: float) -> dict:
    """NBR 15575: iluminação mínima = 1/8 da área do piso."""
    min_required = room_area / 8
    return {
        "window_area_m2": round(window_area, 3),
        "min_required_m2": round(min_required, 3),
        "compliant": window_area >= min_required,
    }


def _wall_placement(wall, position_x: float, sill: float) -> "FreeCAD.Placement":
    """Calcula placement para porta/janela na face da parede."""
    import math

    base = getattr(wall, "Base", None)
    if base is None or not hasattr(base, "Shape") or len(base.Shape.Vertexes) < 2:
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill)),
            FreeCAD.Rotation(),
        )

    start = base.Shape.Vertexes[0].Point
    end   = base.Shape.Vertexes[-1].Point

    dx, dy = end.x - start.x, end.y - start.y
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1e-6:
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill)),
            FreeCAD.Rotation(),
        )

    ux, uy = dx / length, dy / length
    pos = FreeCAD.Vector(
        start.x + ux * mm(position_x),
        start.y + uy * mm(position_x),
        mm(sill),
    )
    angle = math.degrees(math.atan2(dy, dx))
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    return FreeCAD.Placement(pos, rot)


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

    wall = _find_wall(doc, wall_label)

    if wall is None:
        FreeCAD.Console.PrintError(
            f"Parede '{wall_label}' não encontrada.\n"
            f"Dica: o Label é definido no create_room.py como "
            f"'<NomeCômodo>_Parede_<Sul|Norte|Leste|Oeste>'.\n"
        )
        _list_walls(doc)
        return None

    FreeCAD.Console.PrintMessage(f"Parede encontrada: Name={wall.Name!r}  Label={wall.Label!r}\n")

    preset_name = WINDOW_PRESETS.get(window_type, "Open 2-pane")
    if preset_name not in _SAFE_PRESETS:
        FreeCAD.Console.PrintWarning(
            f"Preset '{preset_name}' pode não existir nesta versão do FreeCAD. "
            f"Usando 'Open 2-pane'.\n"
        )
        preset_name = "Open 2-pane"

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
        placement=_wall_placement(wall, position_x, sill_height),
    )

    if window is None:
        FreeCAD.Console.PrintError(
            f"Falha ao criar janela com preset '{preset_name}'. "
            f"Presets disponíveis: {sorted(_SAFE_PRESETS)}\n"
        )
        return None

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
