"""Skills de carpintaria — móveis planejados, madeiras, cálculo de materiais."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class FurnitureItem:
    id: str
    furniture_type: str
    position: list[float]
    width: float
    depth: float
    height: float
    rotation: float = 0.0
    material: str = "MDF"


WOOD_CATALOG = {
    "pinus": {
        "budget": "economico",
        "environments": ["interno"],
        "density_kg_m3": 530,
        "applications": ["estrutural_leve", "móvel", "forro"],
        "description": "Madeira de reflorestamento, leve e fácil de trabalhar.",
    },
    "eucalipto": {
        "budget": "economico",
        "environments": ["interno", "externo"],
        "density_kg_m3": 700,
        "applications": ["estrutural", "deck", "caibro"],
        "description": "Resistente, boa para uso externo com tratamento.",
    },
    "cedro": {
        "budget": "medio",
        "environments": ["interno", "umido"],
        "density_kg_m3": 500,
        "applications": ["móvel", "esquadria", "revestimento"],
        "description": "Aromático, resistente à umidade e insetos.",
    },
    "ipê": {
        "budget": "premium",
        "environments": ["interno", "externo", "umido"],
        "density_kg_m3": 1050,
        "applications": ["deck", "estrutural", "pergolado"],
        "description": "Alta durabilidade natural, ideal para áreas externas.",
    },
    "cumaru": {
        "budget": "premium",
        "environments": ["interno", "externo", "umido"],
        "density_kg_m3": 1000,
        "applications": ["deck", "assoalho", "estrutural"],
        "description": "Durabilidade similar ao ipê, excelente acabamento.",
    },
    "MDF": {
        "budget": "economico",
        "environments": ["interno"],
        "density_kg_m3": 750,
        "applications": ["móvel_planejado", "armario", "bancada"],
        "description": "MDF laminado, ideal para móveis planejados internos.",
    },
    "MDP": {
        "budget": "economico",
        "environments": ["interno"],
        "density_kg_m3": 680,
        "applications": ["armario", "prateleira"],
        "description": "Mais leve que MDF, bom para partes internas de armários.",
    },
    "compensado": {
        "budget": "medio",
        "environments": ["interno", "umido"],
        "density_kg_m3": 600,
        "applications": ["estrutural_leve", "forma", "móvel"],
        "description": "Boa resistência, várias espessuras disponíveis.",
    },
}

FURNITURE_STANDARD_SIZES = {
    "armario_cozinha_alto": {"width": 0.60, "depth": 0.35, "height": 2.10},
    "armario_cozinha_baixo": {"width": 0.60, "depth": 0.55, "height": 0.85},
    "bancada_cozinha": {"width": 0.60, "depth": 0.60, "height": 0.90},
    "armario_banheiro": {"width": 0.80, "depth": 0.35, "height": 0.70},
    "guarda_roupa_solteiro": {"width": 1.20, "depth": 0.50, "height": 2.10},
    "guarda_roupa_casal": {"width": 2.00, "depth": 0.60, "height": 2.10},
    "cama_solteiro": {"width": 0.88, "depth": 1.88, "height": 0.45},
    "cama_casal": {"width": 1.38, "depth": 1.88, "height": 0.45},
    "cama_queen": {"width": 1.58, "depth": 1.98, "height": 0.45},
    "cama_king": {"width": 1.93, "depth": 2.03, "height": 0.45},
    "sofa_2_lugares": {"width": 1.50, "depth": 0.85, "height": 0.85},
    "sofa_3_lugares": {"width": 2.10, "depth": 0.85, "height": 0.85},
    "mesa_jantar_4": {"width": 1.20, "depth": 0.80, "height": 0.75},
    "mesa_jantar_6": {"width": 1.60, "depth": 0.90, "height": 0.75},
    "mesa_escritorio": {"width": 1.40, "depth": 0.70, "height": 0.75},
    "pia_banheiro": {"width": 0.50, "depth": 0.45, "height": 0.85},
    "vaso_sanitario": {"width": 0.37, "depth": 0.65, "height": 0.80},
    "box_banheiro": {"width": 0.90, "depth": 0.90, "height": 2.00},
    "banheira": {"width": 0.80, "depth": 1.60, "height": 0.50},
    "fogao_4_bocas": {"width": 0.56, "depth": 0.56, "height": 0.85},
    "geladeira": {"width": 0.70, "depth": 0.80, "height": 1.80},
}


class CarpentrySkills:
    """Habilidades de carpintaria e móveis planejados."""

    def __init__(self):
        self.furniture_items: dict[str, FurnitureItem] = {}

    def add_furniture(
        self,
        furniture_type: str,
        position: list[float],
        width: float | None = None,
        depth: float | None = None,
        height: float | None = None,
        rotation: float = 0.0,
        material: str = "MDF",
    ) -> dict:
        std = FURNITURE_STANDARD_SIZES.get(furniture_type, {})
        w = width or std.get("width", 1.0)
        d = depth or std.get("depth", 0.60)
        h = height or std.get("height", 0.80)

        item_id = f"furn_{uuid.uuid4().hex[:8]}"
        item = FurnitureItem(
            id=item_id,
            furniture_type=furniture_type,
            position=position,
            width=w,
            depth=d,
            height=h,
            rotation=rotation,
            material=material,
        )
        self.furniture_items[item_id] = item

        return {
            "id": item_id,
            "type": furniture_type,
            "position": position,
            "dimensions": {"width": w, "depth": d, "height": h},
            "rotation_deg": rotation,
            "material": material,
            "footprint_m2": round(w * d, 3),
            "status": "inserido",
        }

    def suggest_wood(
        self,
        application: str,
        budget: str = "medio",
        environment: str = "interno",
    ) -> dict:
        candidates = []
        for name, props in WOOD_CATALOG.items():
            if environment not in props["environments"]:
                continue
            if props["budget"] != budget and budget != "qualquer":
                if budget == "economico" and props["budget"] != "economico":
                    continue
                if budget == "premium" and props["budget"] not in ("medio", "premium"):
                    continue
            candidates.append(
                {
                    "wood": name,
                    "budget": props["budget"],
                    "density_kg_m3": props["density_kg_m3"],
                    "description": props["description"],
                    "applications": props["applications"],
                }
            )

        return {
            "application": application,
            "budget": budget,
            "environment": environment,
            "suggestions": candidates[:3],
        }

    def calculate_materials(
        self,
        furniture_type: str,
        dimensions: dict,
        material: str = "MDF",
        thickness_mm: int = 18,
    ) -> dict:
        w = dimensions.get("width", 1.0)
        h = dimensions.get("height", 0.80)
        d = dimensions.get("depth", 0.60)
        t = thickness_mm / 1000  # converte para metros

        # Estimativa simplificada de chapas para armário/gabinete
        panels = {
            "lateral_esq": d * h,
            "lateral_dir": d * h,
            "topo": (w - 2 * t) * d,
            "base": (w - 2 * t) * d,
            "fundo": w * h * 0.5,  # chapa mais fina (6mm)
            "porta": w * h,
        }
        total_area = sum(panels.values())
        chapa_std_m2 = 2.75 * 1.85  # chapa padrão 2750x1850mm

        density = WOOD_CATALOG.get(material, {}).get("density_kg_m3", 700)
        volume_m3 = total_area * t
        weight_kg = volume_m3 * density

        return {
            "furniture_type": furniture_type,
            "material": material,
            "thickness_mm": thickness_mm,
            "panels": {k: round(v, 3) for k, v in panels.items()},
            "total_area_m2": round(total_area, 3),
            "chapas_needed": round(total_area / chapa_std_m2, 1),
            "estimated_weight_kg": round(weight_kg, 1),
        }

    def get_standard_sizes(self, furniture_type: str) -> dict:
        sizes = FURNITURE_STANDARD_SIZES.get(furniture_type)
        if sizes:
            return {"furniture_type": furniture_type, "standard_sizes_m": sizes}
        return {
            "furniture_type": furniture_type,
            "available_types": list(FURNITURE_STANDARD_SIZES.keys()),
        }
