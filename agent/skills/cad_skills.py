"""Skills de CAD para FreeCAD — paredes, portas, janelas, cotas."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tools.freecad_tools import FreeCadTools
    from ..tools.geometry_tools import GeometryTools


@dataclass
class Wall:
    id: str
    start: list[float]
    end: list[float]
    thickness: float = 0.15
    height: float = 2.80
    material: str = "alvenaria"
    openings: list[dict] = field(default_factory=list)


@dataclass
class Opening:
    id: str
    wall_id: str
    position: float
    width: float
    height: float
    type: str


class CADSkills:
    """Habilidades de desenho CAD para plantas baixas no FreeCAD."""

    WALL_MATERIALS = {
        "alvenaria": {"thickness": 0.15, "hatch": "ANSI31"},
        "drywall": {"thickness": 0.10, "hatch": "ANSI32"},
        "concreto": {"thickness": 0.20, "hatch": "ANSI33"},
        "tijolo_vista": {"thickness": 0.15, "hatch": "BRICK"},
    }

    def __init__(self, freecad: "FreeCadTools", geometry: "GeometryTools"):
        self.freecad = freecad
        self.geometry = geometry
        self.walls: dict[str, Wall] = {}
        self.openings: dict[str, Opening] = {}

    def add_wall(
        self,
        start: list[float],
        end: list[float],
        thickness: float = 0.15,
        height: float = 2.80,
        material: str = "alvenaria",
    ) -> dict:
        wall_id = f"wall_{uuid.uuid4().hex[:8]}"
        mat = self.WALL_MATERIALS.get(material, self.WALL_MATERIALS["alvenaria"])
        thickness = thickness or mat["thickness"]

        wall = Wall(
            id=wall_id,
            start=start,
            end=end,
            thickness=thickness,
            height=height,
            material=material,
        )
        self.walls[wall_id] = wall

        length = self.geometry.distance(start, end)
        return {
            "id": wall_id,
            "start": start,
            "end": end,
            "length_m": round(length, 3),
            "thickness_m": thickness,
            "height_m": height,
            "material": material,
            "area_m2": round(length * height, 2),
            "status": "criada",
        }

    def add_door(
        self,
        wall_id: str,
        position: float,
        width: float,
        height: float = 2.10,
        opening_side: str = "left",
        door_type: str = "simples",
    ) -> dict:
        if wall_id not in self.walls:
            return {"error": f"Parede '{wall_id}' não encontrada"}

        door_id = f"door_{uuid.uuid4().hex[:8]}"
        opening = Opening(
            id=door_id,
            wall_id=wall_id,
            position=position,
            width=width,
            height=height,
            type=f"porta_{door_type}",
        )
        self.openings[door_id] = opening
        self.walls[wall_id].openings.append({"id": door_id, "type": "door"})

        return {
            "id": door_id,
            "wall_id": wall_id,
            "width_m": width,
            "height_m": height,
            "type": door_type,
            "opening_side": opening_side,
            "nbr_min_width": 0.80,
            "compliant": width >= 0.80,
            "status": "inserida",
        }

    def add_window(
        self,
        wall_id: str,
        position: float,
        width: float,
        height: float,
        sill_height: float = 0.90,
        window_type: str = "correr",
    ) -> dict:
        if wall_id not in self.walls:
            return {"error": f"Parede '{wall_id}' não encontrada"}

        win_id = f"win_{uuid.uuid4().hex[:8]}"
        opening = Opening(
            id=win_id,
            wall_id=wall_id,
            position=position,
            width=width,
            height=height,
            type=f"janela_{window_type}",
        )
        self.openings[win_id] = opening
        self.walls[wall_id].openings.append({"id": win_id, "type": "window"})

        illumination_ratio = width * height
        return {
            "id": win_id,
            "wall_id": wall_id,
            "width_m": width,
            "height_m": height,
            "sill_height_m": sill_height,
            "type": window_type,
            "illumination_area_m2": round(illumination_ratio, 3),
            "status": "inserida",
        }

    def add_dimension(
        self,
        start: list[float],
        end: list[float],
        offset: float = 0.50,
    ) -> dict:
        dim_id = f"dim_{uuid.uuid4().hex[:8]}"
        length = self.geometry.distance(start, end)
        return {
            "id": dim_id,
            "start": start,
            "end": end,
            "offset_m": offset,
            "value_m": round(length, 3),
            "status": "inserida",
        }

    def get_summary(self) -> dict:
        return {
            "total_walls": len(self.walls),
            "total_doors": sum(
                1 for o in self.openings.values() if o.type.startswith("porta")
            ),
            "total_windows": sum(
                1 for o in self.openings.values() if o.type.startswith("janela")
            ),
        }
