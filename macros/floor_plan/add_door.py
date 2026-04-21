"""
Macro FreeCAD: Adicionar Porta

Insere uma porta em uma parede existente no documento ativo.
Execute dentro do FreeCAD: Macro → Executar Macro → add_door.py

COMO USAR:
  1. Execute create_room.py primeiro para criar as paredes.
  2. No Report View (Menu Ver → Painéis → Saída do relatório) anote o Label
     da parede onde quer inserir a porta (ex: "Sala de Estar_Parede_Sul").
  3. Cole esse Label em WALL_LABEL abaixo e execute esta macro.
"""

import FreeCAD
import Arch
import Draft

# ── Configurações ──────────────────────────────────────────────────────────────
# Coloque aqui o Label EXATO da parede (veja o Report View após create_room.py)
# Exemplos: "Sala de Estar_Parede_Sul" | "Quarto_Parede_Oeste" | "Wall001"
WALL_LABEL = "Sala de Estar_Parede_Sul"
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


def _find_wall(doc, identifier: str):
    """Busca parede por Label exato, Name exato ou Label parcial (case-insensitive)."""
    walls = [o for o in doc.Objects if hasattr(o, "Width") and hasattr(o, "Height")]

    # 1. Label exato
    for w in walls:
        if w.Label == identifier:
            return w

    # 2. Name interno exato (ex: "Wall001")
    for w in walls:
        if w.Name == identifier:
            return w

    # 3. Label parcial case-insensitive
    identifier_lower = identifier.lower()
    for w in walls:
        if identifier_lower in w.Label.lower():
            return w

    return None


def _list_walls(doc) -> None:
    """Imprime todas as paredes disponíveis no documento."""
    walls = [o for o in doc.Objects if hasattr(o, "Width") and hasattr(o, "Height")]
    if not walls:
        FreeCAD.Console.PrintError("Nenhuma parede encontrada no documento.\n")
        return
    FreeCAD.Console.PrintMessage("Paredes disponíveis no documento:\n")
    for w in walls:
        FreeCAD.Console.PrintMessage(f"  Name={w.Name!r:12s}  Label={w.Label!r}\n")


def _wall_placement(wall, position_x: float, sill: float) -> "FreeCAD.Placement":
    """Calcula placement para porta/janela na face da parede."""
    import math

    base = getattr(wall, "Base", None)
    if base is None or not hasattr(base, "Shape") or len(base.Shape.Vertexes) < 2:
        # Fallback sem geometria da parede
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill)),
            FreeCAD.Rotation(),
        )

    start = base.Shape.Vertexes[0].Point   # já em mm (unidade FreeCAD)
    end   = base.Shape.Vertexes[-1].Point

    dx, dy = end.x - start.x, end.y - start.y
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1e-6:
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position_x), 0, mm(sill)),
            FreeCAD.Rotation(),
        )

    # Vetor unitário ao longo da parede
    ux, uy = dx / length, dy / length

    # Posição no mundo = origem da parede + deslocamento ao longo dela
    pos = FreeCAD.Vector(
        start.x + ux * mm(position_x),
        start.y + uy * mm(position_x),
        mm(sill),
    )

    # makeWindowPreset cria o elemento deitado no plano XY.
    # 1) Ergue 90° em torno de X → elemento fica vertical, face apontando Y+
    # 2) Gira em torno de Z pelo ângulo da parede → alinha com a direção da parede
    rot_upright = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    angle = math.degrees(math.atan2(dy, dx))
    rot_align = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    rot = rot_align.multiply(rot_upright)

    return FreeCAD.Placement(pos, rot)


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
        placement=_wall_placement(wall, position_x, sill),
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
