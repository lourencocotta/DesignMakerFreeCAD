"""
Macro FreeCAD: Planta Baixa — Casa da Árvore em Eucalipto Roliço Tratado

Referência: docs/memorial_casa_arvore.pdf
Área total: 9,00 m²  (cômodo 4,00 m² + varanda em L 5,00 m²)
Execute dentro do FreeCAD: Macro → Executar Macro → casa_arvore.py
"""

import math

import FreeCAD
import Arch
import Draft

# ── Parâmetros gerais ──────────────────────────────────────────────────────────
WALL_T  = 0.10   # espessura parede eucalipto serrado (m)
WALL_H  = 2.00   # altura livre sob telhado (m)
GC_H    = 1.00   # guarda-corpo (m)
PILAR_R = 0.10   # raio pilar ø20cm (m)
BEIRAL  = 0.30   # avanço do beiral (m)
SILL    = 0.90   # peitoril mínimo (m) — NBR 10821
# ──────────────────────────────────────────────────────────────────────────────
# Layout — origin = canto SW da plataforma (metros)
#   Y cresce para Norte, X cresce para Leste
#
#   (0,3)──────────────────────(3,3)    ← varanda norte (1×3 m)
#     │  ▒▒▒▒ VARANDA NORTE ▒▒▒▒  │
#   (0,2)────(1,2)────────────(3,2)
#     │ VAR  │                    │
#     │OESTE │   C Ô M O D O      │   LESTE
#     │1×2m  │   2,00 × 2,00 m    │   (árvore)
#  [PORTA]   │                    │
#   (0,0)────(1,0)────────────(3,0)
#                  [JANELA]
#                    SUL
# ──────────────────────────────────────────────────────────────────────────────


def mm(v: float) -> float:
    return v * 1000


def _make_doc() -> "FreeCAD.Document":
    doc = FreeCAD.ActiveDocument
    if doc is None:
        doc = FreeCAD.newDocument("CasaDaArvore_PlantaBaixa")
    return doc


def _add_arch_wall(
    doc,
    sx: float, sy: float,
    ex: float, ey: float,
    label: str,
    height: float = WALL_H,
    thickness: float = WALL_T,
) -> object:
    line = Draft.makeLine(
        FreeCAD.Vector(mm(sx), mm(sy), 0),
        FreeCAD.Vector(mm(ex), mm(ey), 0),
    )
    line.Label = f"{label}_eixo"
    line.ViewObject.Visibility = False

    wall = Arch.makeWall(line, length=None, width=mm(thickness), height=mm(height))
    wall.Label = label
    try:
        wall.ViewObject.ShapeColor = (0.85, 0.70, 0.50)   # tom eucalipto claro
    except Exception:
        pass
    dist = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2)
    FreeCAD.Console.PrintMessage(
        f"  Parede '{label}': {dist:.2f} m × {thickness} m × {height} m\n"
    )
    return wall


def _find_wall(doc, label: str) -> object:
    for obj in doc.Objects:
        if obj.Label == label:
            return obj
    return None


def _wall_placement(wall, position: float, sill: float) -> "FreeCAD.Placement":
    base = getattr(wall, "Base", None)
    if base is None or not hasattr(base, "Shape") or len(base.Shape.Vertexes) < 2:
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position), 0, mm(sill)),
            FreeCAD.Rotation(),
        )
    start = base.Shape.Vertexes[0].Point
    end   = base.Shape.Vertexes[-1].Point
    dx, dy = end.x - start.x, end.y - start.y
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1e-6:
        return FreeCAD.Placement(
            FreeCAD.Vector(mm(position), 0, mm(sill)),
            FreeCAD.Rotation(),
        )
    ux, uy = dx / length, dy / length
    pos = FreeCAD.Vector(
        start.x + ux * mm(position),
        start.y + uy * mm(position),
        mm(sill),
    )
    rot_upright = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    angle = math.degrees(math.atan2(dy, dx))
    rot_align = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    return FreeCAD.Placement(pos, rot_align.multiply(rot_upright))


def _add_door(doc, wall_label: str, position: float, width: float, height: float, label: str):
    wall = _find_wall(doc, wall_label)
    if wall is None:
        FreeCAD.Console.PrintError(f"Parede '{wall_label}' não encontrada.\n")
        return None
    door = Arch.makeWindowPreset(
        "Simple door",
        width=mm(width), height=mm(height),
        h1=mm(0.1), h2=mm(0.1), h3=mm(0.1),
        w1=mm(0.1), w2=mm(0.1),
        o1=0, o2=mm(0.1),
        placement=_wall_placement(wall, position, 0.0),
    )
    if door:
        door.Label = label
        door.Hosts = [wall]
        FreeCAD.Console.PrintMessage(f"  Porta '{label}': {width} m × {height} m\n")
    return door


def _add_window(
    doc,
    wall_label: str,
    position: float,
    width: float,
    height: float,
    sill: float,
    label: str,
):
    wall = _find_wall(doc, wall_label)
    if wall is None:
        FreeCAD.Console.PrintError(f"Parede '{wall_label}' não encontrada.\n")
        return None
    window = Arch.makeWindowPreset(
        "Open 2-pane",
        width=mm(width), height=mm(height),
        h1=mm(0.05), h2=mm(0.05), h3=mm(0.05),
        w1=mm(0.05), w2=mm(0.05),
        o1=0, o2=mm(0.05),
        placement=_wall_placement(wall, position, sill),
    )
    if window:
        window.Label = label
        window.Hosts = [wall]
        FreeCAD.Console.PrintMessage(
            f"  Janela '{label}': {width} m × {height} m | peitoril={sill} m\n"
        )
    return window


def _add_gc_wire(doc, points: list, label: str, dashed: bool = False) -> object:
    pts = [FreeCAD.Vector(mm(x), mm(y), 0) for x, y in points]
    wire = Draft.makeWire(pts, closed=False)
    wire.Label = label
    try:
        wire.ViewObject.LineColor = (0.35, 0.35, 0.35)
        wire.ViewObject.LineWidth = 2.0
        if dashed:
            wire.ViewObject.DrawStyle = "Dashed"
    except Exception:
        pass
    return wire


def _add_pilar(doc, cx: float, cy: float, label: str) -> object:
    circle = Draft.makeCircle(
        mm(PILAR_R),
        placement=FreeCAD.Placement(
            FreeCAD.Vector(mm(cx), mm(cy), 0),
            FreeCAD.Rotation(),
        ),
    )
    circle.Label = label
    try:
        circle.ViewObject.LineColor = (0.10, 0.10, 0.10)
        circle.ViewObject.LineWidth = 2.5
        circle.ViewObject.ShapeColor = (0.30, 0.20, 0.10)
    except Exception:
        pass
    return circle


def _add_dim(doc, p1, p2, p_mid, label: str) -> object:
    dim = Draft.makeDimension(
        FreeCAD.Vector(*p1),
        FreeCAD.Vector(*p2),
        FreeCAD.Vector(*p_mid),
    )
    dim.Label = label
    try:
        dim.ViewObject.FontSize = 150
        dim.ViewObject.ArrowSize = 80
        dim.ViewObject.ArrowType = "Arrow"
    except Exception:
        pass
    return dim


def _add_text(doc, lines: list, x: float, y: float) -> object:
    text = Draft.makeText(lines, FreeCAD.Vector(mm(x), mm(y), 0))
    try:
        text.ViewObject.FontSize = 120
    except Exception:
        pass
    return text


def build() -> "FreeCAD.Document":
    doc = _make_doc()
    FreeCAD.Console.PrintMessage("\n=== Casa da Árvore — Planta Baixa ===\n")

    # ── 1. Paredes do cômodo (eucalipto serrado 0,10 m) ───────────────────────
    FreeCAD.Console.PrintMessage("— Paredes do cômodo —\n")

    # Sul: (1.00,0.00) → (3.00,0.00)  — janela 0.60×0.60 centrada
    w_sul = _add_arch_wall(doc, 1.00, 0.00, 3.00, 0.00, "Comodo_Parede_Sul")

    # Leste: (3.00,0.00) → (3.00,2.00)  — fechada (fachada próxima à árvore)
    w_leste = _add_arch_wall(doc, 3.00, 0.00, 3.00, 2.00, "Comodo_Parede_Leste")

    # Norte do cômodo: (3.00,2.00) → (1.00,2.00)  — janela 0.60×0.60 ventilação cruzada
    w_norte = _add_arch_wall(doc, 3.00, 2.00, 1.00, 2.00, "Comodo_Parede_Norte")

    # Divisória Oeste cômodo↔varanda: (1.00,2.00) → (1.00,0.00)  — porta 0.70 m
    w_div = _add_arch_wall(doc, 1.00, 2.00, 1.00, 0.00, "Comodo_Divisoria_Oeste")

    doc.recompute()

    # ── 2. Aberturas ──────────────────────────────────────────────────────────
    FreeCAD.Console.PrintMessage("— Aberturas —\n")

    # Janela Sul: 0.60×0.60, peitoril 0.90 m, centrada (parede 2 m → pos=0.70 m)
    _add_window(doc, "Comodo_Parede_Sul", 0.70, 0.60, 0.60, SILL, "Janela_Sul")

    # Janela Norte: ventilação cruzada, 0.60×0.60, peitoril 0.90 m, centrada
    _add_window(doc, "Comodo_Parede_Norte", 0.70, 0.60, 0.60, SILL, "Janela_Norte")

    # Porta Principal Oeste: 0.70 m, h=2.00 m, centrada na divisória (2 m → pos=0.65 m)
    _add_door(doc, "Comodo_Divisoria_Oeste", 0.65, 0.70, 2.00, "Porta_Principal")

    doc.recompute()

    # ── 3. Guarda-corpo das varandas (h=1.00 m) ───────────────────────────────
    FreeCAD.Console.PrintMessage("— Guarda-corpo —\n")

    # Norte exterior: Y=3.00, X: 0→3 (completo)
    _add_gc_wire(doc, [(0.00, 3.00), (3.00, 3.00)], "GC_Norte_Exterior")

    # Oeste completo: X=0, Y: 0→3 (varanda oeste + limite da varanda norte)
    _add_gc_wire(doc, [(0.00, 0.00), (0.00, 3.00)], "GC_Oeste_Exterior")

    # Sul da varanda oeste: Y=0, X: 0→1 (ponto de acesso escada de marinheiro)
    _add_gc_wire(doc, [(0.00, 0.00), (1.00, 0.00)], "GC_Var_Oeste_Sul")

    # Leste da varanda norte: X=3, Y: 2→3 (fecha canto NE da varanda)
    _add_gc_wire(doc, [(3.00, 2.00), (3.00, 3.00)], "GC_Var_Norte_Leste")

    # ── 4. Pilares ø20 cm (6 unidades: 4 cantos + 2 intermediários) ───────────
    FreeCAD.Console.PrintMessage("— Pilares ø20 cm —\n")
    pilares = [
        (0.00, 0.00, "P3_SW"),
        (1.50, 0.00, "Pi2_S_centro"),
        (3.00, 0.00, "P4_SE"),
        (0.00, 3.00, "P1_NW"),
        (1.50, 3.00, "Pi1_N_centro"),
        (3.00, 3.00, "P2_NE"),
    ]
    for cx, cy, name in pilares:
        _add_pilar(doc, cx, cy, f"Pilar_{name}")
        FreeCAD.Console.PrintMessage(f"  Pilar {name}: ({cx},{cy})\n")

    # ── 5. Projeção do beiral (0,30 m além de cada fachada) — tracejado ───────
    b = BEIRAL
    beiral_pts = [
        (-b, -b), (3.00 + b, -b),
        (3.00 + b, 3.00 + b), (-b, 3.00 + b), (-b, -b),
    ]
    _add_gc_wire(doc, beiral_pts, "Beiral_0.30m", dashed=True)

    # Cumeeira (projeção em planta): Y=1.50 (meio do vão N-S), X: -0.30→3.30
    cumeeira_pts = [(-b, 1.50), (3.00 + b, 1.50)]
    _add_gc_wire(doc, cumeeira_pts, "Cumeeira_proj", dashed=True)

    # ── 6. Cotas ──────────────────────────────────────────────────────────────
    FreeCAD.Console.PrintMessage("— Cotas —\n")
    O = -0.50   # offset das cotas para fora da planta (m)

    # Largura do cômodo (L-O, parede sul): X: 1→3 em Y=-0.50
    _add_dim(doc, (mm(1.00), mm(O), 0), (mm(3.00), mm(O), 0),
             (mm(2.00), mm(O), 0), "Cota_Comodo_L")

    # Largura total da planta: X: 0→3 em Y=-0.90
    _add_dim(doc, (mm(0.00), mm(O - 0.40), 0), (mm(3.00), mm(O - 0.40), 0),
             (mm(1.50), mm(O - 0.40), 0), "Cota_Total_L")

    # Largura varanda oeste: X: 0→1 em Y=-0.50
    _add_dim(doc, (mm(0.00), mm(O), 0), (mm(1.00), mm(O), 0),
             (mm(0.50), mm(O), 0), "Cota_VarOeste_L")

    # Profundidade cômodo: Y: 0→2 em X=3.50
    _add_dim(doc, (mm(3.50), mm(0.00), 0), (mm(3.50), mm(2.00), 0),
             (mm(3.50), mm(1.00), 0), "Cota_Comodo_P")

    # Profundidade varanda norte: Y: 2→3 em X=3.50
    _add_dim(doc, (mm(3.50), mm(2.00), 0), (mm(3.50), mm(3.00), 0),
             (mm(3.50), mm(2.50), 0), "Cota_VarNorte_P")

    # Profundidade total: Y: 0→3 em X=4.00
    _add_dim(doc, (mm(4.00), mm(0.00), 0), (mm(4.00), mm(3.00), 0),
             (mm(4.00), mm(1.50), 0), "Cota_Total_P")

    # ── 7. Labels de texto ────────────────────────────────────────────────────
    _add_text(doc, ["CÔMODO", "2,00 × 2,00 m = 4,00 m²"], 2.00, 1.00)
    _add_text(doc, ["VARANDA", "OESTE", "1,00 × 2,00 m"], 0.50, 1.00)
    _add_text(doc, ["VARANDA NORTE — 3,00 × 1,00 m = 3,00 m²"], 1.50, 2.50)
    _add_text(doc, ["↑ NORTE"], 1.40, 3.80)
    _add_text(doc, ["← OESTE (entrada)"], -0.10, -0.30)
    _add_text(doc, ["LESTE → (árvore, dist. mín. 30 cm)"], 3.10, 1.00)
    _add_text(doc, ["Pilares ø20 cm CCB Cl.IV"], 0.80, -1.10)
    _add_text(doc, ["Parede eucalipto serrado e=10 cm / h=2,00 m"], 0.40, -1.40)
    _add_text(doc, ["Beiral 0,30 m (tracejado)"], 0.40, -1.70)
    _add_text(doc, ["Esc. 1:50 — Casa da Árvore em Eucalipto Roliço"], 0.00, -2.10)

    doc.recompute()

    FreeCAD.Console.PrintMessage(
        "\n=== Planta concluída ===\n"
        "  Cômodo:       2,00 × 2,00 m = 4,00 m²\n"
        "  Var. Oeste:   1,00 × 2,00 m = 2,00 m²\n"
        "  Var. Norte:   3,00 × 1,00 m = 3,00 m²\n"
        "  TOTAL:                        9,00 m²\n"
        "  Beiral: 0,30 m | Cumeeira: L-O (proj. Y=1,50 m)\n"
        "  Pilares: 6 × ø20 cm (4 cantos + 2 intermediários a X=1,50 m)\n"
    )

    try:
        import FreeCADGui
        FreeCADGui.ActiveDocument.ActiveView.viewTop()
        FreeCADGui.ActiveDocument.ActiveView.fitAll()
    except Exception:
        pass

    return doc


if __name__ == "__main__":
    build()
