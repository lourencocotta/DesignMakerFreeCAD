"""
Normas brasileiras aplicadas a plantas baixas residenciais.

Referências:
  - NBR 6492:1994 — Representação de projetos de arquitetura
  - NBR 9050:2020 — Acessibilidade
  - NBR 15575:2021 — Desempenho de edificações
  - NBR 10821:2017 — Esquadrias para edificações
"""

from __future__ import annotations

# ─── NBR 6492 — Escalas recomendadas ────────────────────────────────────────

RECOMMENDED_SCALES = {
    "planta_baixa": [50, 75, 100],
    "elevacao": [50, 100],
    "detalhe": [5, 10, 20, 25],
    "implantacao": [200, 500, 1000],
    "situacao": [1000, 2000],
}

# ─── NBR 9050 — Acessibilidade ───────────────────────────────────────────────

ACCESSIBILITY = {
    "porta_min_width_m": 0.80,
    "porta_acessivel_width_m": 0.90,
    "corredor_min_width_m": 0.90,
    "corredor_cadeirante_m": 1.20,
    "rampa_max_inclinacao_pct": 8.33,
    "desnivel_max_sem_rampa_m": 0.005,
    "banheiro_acessivel_area_m2": 4.00,
    "area_giro_cadeirante_diametro_m": 1.50,
}

# ─── NBR 15575 — Dimensões mínimas de cômodos ───────────────────────────────

ROOM_MINIMUMS = {
    "quarto_casal": {
        "area_m2": 9.00,
        "min_width_m": 2.50,
        "pe_direito_m": 2.40,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
    "quarto_solteiro": {
        "area_m2": 7.50,
        "min_width_m": 2.00,
        "pe_direito_m": 2.40,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
    "sala": {
        "area_m2": 11.00,
        "min_width_m": 2.40,
        "pe_direito_m": 2.40,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
    "cozinha": {
        "area_m2": 5.50,
        "min_width_m": 1.80,
        "pe_direito_m": 2.40,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
    "banheiro": {
        "area_m2": 3.50,
        "min_width_m": 1.20,
        "pe_direito_m": 2.20,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
    "area_servico": {
        "area_m2": 2.00,
        "min_width_m": 1.20,
        "pe_direito_m": 2.20,
        "iluminacao_min_pct": 12.5,
        "ventilacao_min_pct": 8.0,
    },
}

# ─── NBR 10821 — Esquadrias ──────────────────────────────────────────────────

WINDOW_STANDARDS = {
    "peitoril_residencial_m": 0.90,
    "peitoril_comercial_m": 1.10,
    "altura_min_janela_m": 0.60,
    "largura_min_janela_m": 0.40,
}

# ─── Utilitários de verificação ──────────────────────────────────────────────


def check_room(room_type: str, area_m2: float, width_m: float) -> dict:
    mins = ROOM_MINIMUMS.get(room_type)
    if not mins:
        return {"status": "norma_nao_mapeada", "room_type": room_type}

    issues = []
    if area_m2 < mins["area_m2"]:
        issues.append(
            f"Área {area_m2:.2f}m² < mínimo {mins['area_m2']}m² (NBR 15575)"
        )
    if width_m < mins["min_width_m"]:
        issues.append(
            f"Largura {width_m:.2f}m < mínimo {mins['min_width_m']}m (NBR 15575)"
        )

    return {
        "room_type": room_type,
        "area_m2": area_m2,
        "width_m": width_m,
        "compliant": len(issues) == 0,
        "issues": issues,
        "reference": "NBR 15575:2021",
    }


def required_window_area(room_area_m2: float, room_type: str = "generico") -> dict:
    """Calcula área mínima de janelas (iluminação e ventilação) por NBR 15575."""
    mins = ROOM_MINIMUMS.get(room_type, {"iluminacao_min_pct": 12.5, "ventilacao_min_pct": 8.0})
    ilum = room_area_m2 * mins["iluminacao_min_pct"] / 100
    vent = room_area_m2 * mins["ventilacao_min_pct"] / 100
    return {
        "room_area_m2": room_area_m2,
        "min_illumination_area_m2": round(ilum, 3),
        "min_ventilation_area_m2": round(vent, 3),
        "reference": "NBR 15575:2021",
    }


def check_accessibility(door_width_m: float, corridor_width_m: float | None = None) -> dict:
    issues = []
    acc = ACCESSIBILITY

    if door_width_m < acc["porta_min_width_m"]:
        issues.append(f"Porta {door_width_m}m abaixo do mínimo {acc['porta_min_width_m']}m (NBR 9050)")

    if corridor_width_m is not None and corridor_width_m < acc["corredor_min_width_m"]:
        issues.append(
            f"Corredor {corridor_width_m}m abaixo do mínimo {acc['corredor_min_width_m']}m (NBR 9050)"
        )

    return {
        "door_width_m": door_width_m,
        "corridor_width_m": corridor_width_m,
        "accessible_door": door_width_m >= acc["porta_acessivel_width_m"],
        "compliant": len(issues) == 0,
        "issues": issues,
        "reference": "NBR 9050:2020",
    }
