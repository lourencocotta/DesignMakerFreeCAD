"""Skills de planta baixa — criação de cômodos e verificação de normas NBR."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cad_skills import CADSkills
    from .carpentry_skills import CarpentrySkills

# NBR 6492 e NBR 15575 — dimensões mínimas por tipo de cômodo
NBR_MINIMUMS = {
    "quarto_solteiro": {"area_m2": 7.50, "width_m": 2.00},
    "quarto_casal": {"area_m2": 9.00, "width_m": 2.50},
    "sala": {"area_m2": 11.00, "width_m": 2.40},
    "cozinha": {"area_m2": 5.50, "width_m": 1.80},
    "banheiro": {"area_m2": 3.50, "width_m": 1.20},
    "lavabo": {"area_m2": 1.20, "width_m": 0.90},
    "corredor": {"area_m2": None, "width_m": 0.90},
    "garagem": {"area_m2": 10.00, "width_m": 2.40},
    "area_servico": {"area_m2": 2.00, "width_m": 1.20},
}

ROOM_COLORS = {
    "sala": "#FFE4B5",
    "quarto_solteiro": "#ADD8E6",
    "quarto_casal": "#87CEEB",
    "cozinha": "#98FB98",
    "banheiro": "#DDA0DD",
    "lavabo": "#EE82EE",
    "garagem": "#D3D3D3",
    "corredor": "#F5F5DC",
    "area_servico": "#F0E68C",
}


class FloorPlanSkills:
    """Habilidades para composição de planta baixa completa."""

    def __init__(self, cad: "CADSkills", carpentry: "CarpentrySkills"):
        self.cad = cad
        self.carpentry = carpentry
        self.rooms: list[dict] = []

    def add_room(
        self,
        name: str,
        origin: list[float],
        width: float,
        depth: float,
        wall_thickness: float = 0.15,
    ) -> dict:
        x, y = origin
        t = wall_thickness

        # Cria as 4 paredes do cômodo
        walls = [
            self.cad.add_wall([x, y], [x + width, y], t),          # sul
            self.cad.add_wall([x + width, y], [x + width, y + depth], t),  # leste
            self.cad.add_wall([x + width, y + depth], [x, y + depth], t),  # norte
            self.cad.add_wall([x, y + depth], [x, y], t),          # oeste
        ]

        area = width * depth
        room_type = self._classify_room(name)
        compliance = self.check_nbr_compliance(room_type, area, min(width, depth))

        room_data = {
            "name": name,
            "type": room_type,
            "origin": origin,
            "width_m": width,
            "depth_m": depth,
            "area_m2": round(area, 2),
            "wall_ids": [w["id"] for w in walls],
            "color": ROOM_COLORS.get(room_type, "#FFFFFF"),
            "nbr_compliance": compliance,
        }
        self.rooms.append(room_data)
        return room_data

    def check_nbr_compliance(
        self, room_type: str, area: float, width: float | None = None
    ) -> dict:
        minimums = NBR_MINIMUMS.get(room_type)
        if not minimums:
            return {"room_type": room_type, "status": "norma_nao_mapeada"}

        issues = []
        if minimums["area_m2"] and area < minimums["area_m2"]:
            issues.append(
                f"Área {area:.2f}m² abaixo do mínimo {minimums['area_m2']}m² (NBR)"
            )
        if width and minimums["width_m"] and width < minimums["width_m"]:
            issues.append(
                f"Largura {width:.2f}m abaixo do mínimo {minimums['width_m']}m (NBR)"
            )

        return {
            "room_type": room_type,
            "area_m2": round(area, 2),
            "min_area_m2": minimums["area_m2"],
            "min_width_m": minimums["width_m"],
            "compliant": len(issues) == 0,
            "issues": issues,
        }

    def get_program_summary(self) -> dict:
        total_area = sum(r["area_m2"] for r in self.rooms)
        non_compliant = [r for r in self.rooms if not r["nbr_compliance"].get("compliant", True)]
        return {
            "total_rooms": len(self.rooms),
            "total_area_m2": round(total_area, 2),
            "rooms": [
                {"name": r["name"], "area_m2": r["area_m2"], "compliant": r["nbr_compliance"].get("compliant")}
                for r in self.rooms
            ],
            "non_compliant_rooms": [r["name"] for r in non_compliant],
        }

    @staticmethod
    def _classify_room(name: str) -> str:
        name_lower = name.lower()
        mapping = {
            "quarto_casal": ["quarto casal", "suite", "suíte", "master"],
            "quarto_solteiro": ["quarto", "dormitório", "infantil"],
            "sala": ["sala", "living", "estar", "jantar"],
            "cozinha": ["cozinha", "copa"],
            "banheiro": ["banheiro", "wc", "lavabo social"],
            "lavabo": ["lavabo", "half bath"],
            "garagem": ["garagem", "cocheira", "vaga"],
            "corredor": ["corredor", "hall", "circulação"],
            "area_servico": ["serviço", "lavanderia", "área de serviço"],
        }
        for room_type, keywords in mapping.items():
            if any(kw in name_lower for kw in keywords):
                return room_type
        return "outro"
