import FreeCAD
import FreeCADGui
import Draft
import Arch
from FreeCAD import Vector

doc = FreeCAD.newDocument("Celeiro_Multifuncional")


def mm(v):
    return v * 1000


# ──────────────────────────────────────────────────────────────────────────────
# Primitivos de desenho
# ──────────────────────────────────────────────────────────────────────────────

def _wall(p1, p2, height, thickness, name):
    line = Draft.makeLine(Vector(p1[0], p1[1], 0), Vector(p2[0], p2[1], 0))
    return Arch.makeWall(line, length=None, width=thickness, height=height, name=name)


def _preset():
    candidates = [p for p in Arch.WindowPresets if "Simple" in p]
    return candidates[0] if candidates else Arch.WindowPresets[0]


def _opening(width, height, sill, thickness, pos, rot_deg, label, host_wall):
    """Cria ArchWindow/Door e hospeda na parede correta via Arch.insertWindow."""
    w = Arch.makeWindowPreset(
        _preset(),
        width=width, height=height,
        h1=sill, h2=100, h3=100,
        w1=thickness, w2=100, o1=0, o2=0,
    )
    w.Placement = FreeCAD.Placement(pos, FreeCAD.Rotation(Vector(0, 0, 1), rot_deg))
    w.Label = label
    if host_wall is not None:
        Arch.insertWindow(w, host_wall)
    doc.recompute()
    return w


def _rect_wire(x1, y1, x2, y2, label, dashed=False):
    """Wire fechado — sem preenchimento (Wireframe)."""
    pts = [
        Vector(x1, y1, 0), Vector(x2, y1, 0),
        Vector(x2, y2, 0), Vector(x1, y2, 0),
        Vector(x1, y1, 0),
    ]
    wire = Draft.makeWire(pts, closed=True)
    wire.Label = label
    try:
        wire.ViewObject.DisplayMode = "Wireframe"
        if dashed:
            wire.ViewObject.LineStyle = "Dashed"
    except Exception:
        pass
    return wire


def _door_arc(cx, cy, radius, start_deg, end_deg, label):
    """Arco de abertura de porta (90°)."""
    arc = Draft.makeCircle(
        radius,
        placement=FreeCAD.Placement(Vector(cx, cy, 0), FreeCAD.Rotation()),
        face=False,
        startangle=start_deg,
        endangle=end_deg,
    )
    arc.Label = label
    return arc


def _circle(cx, cy, r, label):
    c = Draft.makeCircle(
        r,
        placement=FreeCAD.Placement(Vector(cx, cy, 0), FreeCAD.Rotation()),
        face=False,
    )
    c.Label = label
    return c


def _line(p1, p2, label):
    w = Draft.makeWire([Vector(p1[0], p1[1], 0), Vector(p2[0], p2[1], 0)], closed=False)
    w.Label = label
    return w


def _dim_h(x1, x2, y, label=None):
    d = Draft.makeDimension(
        Vector(x1, y, 0), Vector(x2, y, 0),
        Vector((x1 + x2) / 2, y - 400, 0),
    )
    if label:
        d.Label = label
    return d


def _dim_v(y1, y2, x, label=None):
    d = Draft.makeDimension(
        Vector(x, y1, 0), Vector(x, y2, 0),
        Vector(x + 400, (y1 + y2) / 2, 0),
    )
    if label:
        d.Label = label
    return d


def _text(msg, pos):
    return Draft.makeText(msg.split("\n"), point=Vector(pos[0], pos[1], 0))


# ──────────────────────────────────────────────────────────────────────────────
# 1. Paredes perimetrais
# ──────────────────────────────────────────────────────────────────────────────

def create_envelope():
    """Retorna dict com referências às 4 paredes externas."""
    t, h = 200, 3500
    return {
        "sul":   _wall([0, 0],       [mm(8.5), 0],      h, t, "Parede_Sul"),
        "leste": _wall([mm(8.5), 0], [mm(8.5), mm(10)], h, t, "Parede_Leste"),
        "norte": _wall([0, mm(10)],  [mm(8.5), mm(10)], h, t, "Parede_Norte"),
        "oeste": _wall([0, 0],       [0, mm(10)],        h, t, "Parede_Oeste"),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 2. Bloco de serviços
# ──────────────────────────────────────────────────────────────────────────────

def create_service_block():
    """Paredes internas do bloco de serviços. Retorna dict de paredes."""
    h = 2200
    walls = {
        "transversal": _wall([0, mm(7.5)],    [mm(8.5), mm(7.5)], h, 200, "Parede_Transversal"),
        "comodo_dir":  _wall([mm(6), mm(7.5)], [mm(6), mm(10)],   h, 150, "Parede_Comodo_Dir"),
        "ban_esq":     _wall([7300, 8800],     [7300, mm(10)],     h, 100, "Parede_Banheiro_Esq"),
        "ban_front":   _wall([7300, 8800],     [mm(8.5), 8800],   h, 100, "Parede_Banheiro_Front"),
        "wc_esq":      _wall([6200, 8800],     [6200, mm(10)],    h, 100, "Parede_WC_Esq"),
        "wc_front":    _wall([6200, 8800],     [7300, 8800],      h, 100, "Parede_WC_Front"),
    }
    # Escada ao mezanino
    esc = _rect_wire(200, 7700, 1000, 9500, "ESC. MEZANINO 0,90m")
    try:
        esc.ViewObject.DisplayMode = "Flat Lines"
    except Exception:
        pass
    return walls


# ──────────────────────────────────────────────────────────────────────────────
# 3. Aberturas (portão, portas, janelas) — hospedadas nas paredes
# ──────────────────────────────────────────────────────────────────────────────

def add_openings(env, svc):
    t_ext, t_san = 200, 100

    # Portão principal 4,00 × 3,20 m (fachada sul)
    _opening(4000, 3200, 0,   t_ext, Vector(2250, 0, 0),        0,  "Portao_Principal_4x3.2m",  env["sul"])
    # Porta de serviço 1,00 m (parede oeste)
    _opening(1000, 2100, 0,   t_ext, Vector(0, 3000, 0),       90,  "Porta_Servico_1x2.1m",     env["oeste"])
    # Porta cômodo 0,90 m (parede transversal)
    _opening(900,  2100, 0,   200,   Vector(2550, mm(7.5), 0),  0,  "Porta_Comodo_0.9m",        svc["transversal"])
    # Porta banheiro 0,80 m
    _opening(800,  2100, 0,   t_san, Vector(7750, 8800, 0),     0,  "Porta_Banheiro_0.8m",      svc["ban_front"])
    # Porta WC 0,80 m
    _opening(800,  2100, 0,   t_san, Vector(6250, 8800, 0),     0,  "Porta_WC_0.8m",            svc["wc_front"])
    # Janela cômodo 1,00 × 1,20 m (parede oeste)
    _opening(1000, 1200, 900, t_ext, Vector(0, 8250, 900),     90,  "Janela_Comodo_1x1.2m",     env["oeste"])
    # Janelas galpão — parede leste (2 × 2,00 m)
    for cy, name in [(1800, "Janela_Leste_L1"), (5500, "Janela_Leste_L2")]:
        _opening(2000, 1400, 1200, t_ext, Vector(mm(8.5), cy - 1000, 1200), -90, name, env["leste"])
    # Janelas galpão — parede oeste (2 × 2,00 m + 1 × 1,00 m)
    for cy, w, name in [
        (1800, 2000, "Janela_Oeste_O1"),
        (5500, 2000, "Janela_Oeste_O2"),
        (6800, 1000, "Janela_Oeste_O3"),
    ]:
        _opening(w, 1400, 1200, t_ext, Vector(0, cy - w / 2, 1200), 90, name, env["oeste"])
    # Janelas basculantes sanitários (parede leste)
    _opening(400, 600, 1200, t_ext, Vector(mm(8.5), 9200, 1200), -90, "Janela_Banheiro_0.4x0.6", env["leste"])
    _opening(400, 600, 1200, t_ext, Vector(mm(8.5), 9550, 1200), -90, "Janela_WC_0.4x0.6",       env["leste"])


# ──────────────────────────────────────────────────────────────────────────────
# 4. Arcos de abertura das portas
# ──────────────────────────────────────────────────────────────────────────────

def add_door_arcs():
    # Porta cômodo: dobradiça em X=2550 Y=7500, abre para interior do cômodo (Y+)
    _door_arc(2550, mm(7.5), 900,  0, 90,  "Arco_Porta_Comodo")
    # Linha da folha da porta cômodo
    _line([2550, mm(7.5)], [2550, mm(7.5) + 900], "Folha_Porta_Comodo")

    # Porta banheiro: dobradiça em X=8500 Y=8800, abre para área aberta (Y-)
    _door_arc(mm(8.5) - 200, 8800, 800, 90, 180, "Arco_Porta_Banheiro")
    _line([mm(8.5) - 200, 8800], [mm(8.5) - 200 - 800, 8800], "Folha_Porta_Banheiro")

    # Porta WC: dobradiça em X=6200 Y=8800, abre para área aberta (Y-)
    _door_arc(6250, 8800, 800, 0, 90, "Arco_Porta_WC")
    _line([6250, 8800], [6250 + 800, 8800], "Folha_Porta_WC")

    # Porta de serviço: dobradiça em X=0 Y=3000, abre para interior do galpão (X+)
    _door_arc(0, 3000, 1000, -90, 0, "Arco_Porta_Servico")
    _line([0, 3000], [0, 3000 + 1000], "Folha_Porta_Servico")


# ──────────────────────────────────────────────────────────────────────────────
# 5. Mezanino — contorno tracejado + guarda-corpo
# ──────────────────────────────────────────────────────────────────────────────

def add_mezanino():
    # Contorno tracejado sobre o cômodo (projeção do mezanino)
    _rect_wire(0, mm(7.5), mm(6), mm(10), "MEZANINO 15,00 m²", dashed=True)

    # Guarda-corpo frontal do mezanino (NBR 9077, h=1,10 m)
    # Representado na planta como linha dupla na borda Y=7500
    _line([200, mm(7.5) + 100], [mm(6) - 200, mm(7.5) + 100], "Guarda_Corpo_Mezanino")
    _line([200, mm(7.5) + 220], [mm(6) - 200, mm(7.5) + 220], "Guarda_Corpo_Mezanino_2")
    _text("GC h=1,10m\n(NBR 9077)", [1000, mm(7.5) + 300])


# ──────────────────────────────────────────────────────────────────────────────
# 6. Zona de abate — canto NE do galpão
# ──────────────────────────────────────────────────────────────────────────────

def add_slaughter_zone():
    # Demarcação: X 5800→8300, Y 6200→7300 (canto NE, junto à parede transversal)
    _rect_wire(5800, 6200, 8300, 7300, "ZONA DE ABATE")
    # Canaleta longitudinal com caimento 2%
    _line([5800, 6750], [8300, 6750], "CANALETA c/ GRELHA 200mm")
    # Trilho de içamento (I-150, h=3,50 m — projeção em planta)
    _line([5800, 6750], [8300, 6750], "TRILHO ABATE I-150 h=3,50m")
    # 2 pontos de água (torneiras) na zona de abate
    _circle(6200, 6400, 80, "Torneira_Abate_1")
    _circle(7800, 6400, 80, "Torneira_Abate_2")
    _text("2 pts água ¾\"", [6600, 6300])


# ──────────────────────────────────────────────────────────────────────────────
# 7. Instalações hidráulicas e sanitárias (externas)
# ──────────────────────────────────────────────────────────────────────────────

def add_hydraulic_symbols():
    # Reservatório elevado 2.000 L — externo, lado leste, Y≈7000
    _rect_wire(9000, 6500, 10200, 7700, "Reservatorio_2000L")
    _text("RES. 2.000 L\nELEVADO h=3,0m", [9100, 7000])

    # Caixa de gordura — externa, próxima da área aberta (fachada norte)
    _rect_wire(9000, 9400, 9600, mm(10), "Caixa_Gordura")
    _text("CX. GORDURA", [9050, 9600])

    # Caixa de inspeção
    _rect_wire(9000, 8500, 9500, 9000, "Caixa_Inspecao")
    _text("CX. INSP.", [9050, 8650])

    # Fossa séptica (NBR 7229, até 5 usuários)
    _circle(10800, 8000, 700, "Fossa_Septica")
    _text("FOSSA SÉPTICA\n+ FILTRO\n(NBR 7229)", [10200, 7600])

    # Ligação fossa (linha tracejada)
    fs = _line([9500, 8750], [10100, 8000], "Ramal_Esgoto")
    try:
        fs.ViewObject.LineStyle = "Dashed"
    except Exception:
        pass

    # Ponto externo de lavagem ¾″ (parede oeste, externo)
    _circle(-300, 1500, 80, "Torneira_Externa_Lavagem")
    _text("Pto. Lavagem ¾\"", [-800, 1350])

    # Calha / descida d'água pluvial (representação nos cantos)
    for pos in [(-150, 200), (mm(8.5) + 150, 200), (-150, mm(10) - 200), (mm(8.5) + 150, mm(10) - 200)]:
        _circle(pos[0], pos[1], 120, "Descida_Aguas_Pluviais")


# ──────────────────────────────────────────────────────────────────────────────
# 8. Instalações elétricas
# ──────────────────────────────────────────────────────────────────────────────

def add_electrical_symbols():
    # Quadro de distribuição (QD) — parede oeste, h=1,50 m do piso
    _rect_wire(100, 4300, 500, 4700, "QD_Quadro_Distribuicao")
    _text("QD", [150, 4420])

    # 4 tomadas 220 V carpintaria (símbolos ao longo da bancada)
    for x in [600, 1200, 1800, 2400]:
        _circle(x, 850, 60, "Tomada_220V_Carpintaria")
    _text("4x Tom. 220V/20A", [800, 950])

    # Ponto de tomada área aberta (com proteção DR)
    _circle(6500, 9400, 60, "Tomada_Area_Aberta_DR")
    _text("Tom. DR", [6550, 9300])

    # Luminárias estanques zona de abate (IP65)
    for x in [6500, 7500]:
        _circle(x, 6600, 100, "Luminaria_Estanque_IP65")
    _text("2x Lum. IP65", [6700, 6500])


# ──────────────────────────────────────────────────────────────────────────────
# 9. Mobiliário
# ──────────────────────────────────────────────────────────────────────────────

def add_furniture_symbols():
    _rect_wire(200,  200,  3200, 800,    "Bancada_Carpintaria")
    _rect_wire(6950, 9550, 7550, mm(10), "Pia_Area_Aberta")
    _rect_wire(6400, 9275, 6800, 9925,   "Vaso_Sanitario")
    _circle(7900, 9400, 450, "Chuveiro")


# ──────────────────────────────────────────────────────────────────────────────
# 10. Cotas e labels
# ──────────────────────────────────────────────────────────────────────────────

def add_dimensions_labels():
    # Cotas externas
    _dim_h(0,       mm(8.5),       y=-1200,          label="8500 mm")
    _dim_v(0,       mm(10),        x=mm(8.5) + 1400, label="10000 mm")
    _dim_h(0,       mm(6),         y=mm(10) + 800,   label="Cômodo 6000 mm")
    _dim_v(mm(7.5), mm(10),        x=-1400,           label="2500 mm")
    # Portão
    _dim_h(2250,    6250,          y=-600,            label="Portão 4000 mm")
    # Sanitários
    _dim_h(7300,    mm(8.5),       y=mm(10) + 500,   label="1200 mm")
    _dim_h(6200,    7300,          y=mm(10) + 500,   label="1100 mm")

    # Labels de ambientes
    _text("GALPÃO PRINCIPAL\n~53,00 m²",          [4250, 3750])
    _text("CÔMODO\n15,00 m²",                      [2500, 8400])
    _text("MEZANINO s/ laje\n15,00 m²",            [2500, 9200])
    _text("ÁREA ABERTA\nC/ PIA",                   [6400, 8100])
    _text("BANHEIRO\n1,44 m²",                     [7400, 9200])
    _text("W.C.\n1,44 m²",                         [6300, 9200])
    _text("ZONA DE ABATE",                         [6000, 6900])
    _text("BANCADA CARPINTARIA",                   [1200, 400])

    # Norte
    Draft.makeText(["N ↑"], point=Vector(9200, 9500, 0)).Label = "Norte"


# ──────────────────────────────────────────────────────────────────────────────
# 11. Carimbo / título
# ──────────────────────────────────────────────────────────────────────────────

def add_title_block():
    # Carimbo posicionado abaixo do desenho (Y negativo)
    bx1, by1, bx2, by2 = 0, -4500, mm(8.5), -2000

    # Borda externa
    _rect_wire(bx1, by1, bx2, by2, "Carimbo_Borda")

    # Divisórias internas
    _line([bx1, -3000], [bx2, -3000], "Carimbo_Div1")
    _line([bx1, -2500], [bx2, -2500], "Carimbo_Div2")
    _line([4250, -3000], [4250, by2],  "Carimbo_Div3")

    # Textos
    _text("CELEIRO MULTIFUNCIONAL RURAL\nPLANTA BAIXA — TÉRREO",      [200, -2350])
    _text("ESC. 1:50",                                                  [4500, -2350])
    _text("Proprietário: A definir\nLocalização: Propriedade rural",    [200, -3400])
    _text("Data: Abril/2026\nRev.: 00",                                 [4500, -3400])
    _text("Área total coberta: 85,00 m²  |  Área com mezanino: ~100,00 m²", [200, -4300])
    _text("NBR 6492 | NBR 9050 | NBR 9077 | NBR 15575",                [200, -4050])


# ──────────────────────────────────────────────────────────────────────────────
def main():
    env = create_envelope()
    svc = create_service_block()
    add_openings(env, svc)
    add_door_arcs()
    add_mezanino()
    add_slaughter_zone()
    add_furniture_symbols()
    add_hydraulic_symbols()
    add_electrical_symbols()
    add_dimensions_labels()
    add_title_block()

    doc.recompute()
    FreeCADGui.activeDocument().activeView().viewTop()
    FreeCADGui.SendMsgToActiveView("ViewFit")


main()
