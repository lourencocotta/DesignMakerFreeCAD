"""Testes unitários para o DesignerAgent e suas skills."""

import pytest
from unittest.mock import MagicMock, patch

from agent.skills.cad_skills import CADSkills
from agent.skills.carpentry_skills import CarpentrySkills
from agent.skills.floor_plan_skills import FloorPlanSkills
from agent.tools.geometry_tools import GeometryTools
from agent.tools.freecad_tools import FreeCadTools


@pytest.fixture
def geometry():
    return GeometryTools()


@pytest.fixture
def freecad():
    return FreeCadTools()


@pytest.fixture
def cad(freecad, geometry):
    return CADSkills(freecad, geometry)


@pytest.fixture
def carpentry():
    return CarpentrySkills()


@pytest.fixture
def floor_plan(cad, carpentry):
    return FloorPlanSkills(cad, carpentry)


# ─── GeometryTools ───────────────────────────────────────────────────────────

class TestGeometryTools:
    def test_distance_horizontal(self, geometry):
        assert geometry.distance([0, 0], [5, 0]) == pytest.approx(5.0)

    def test_distance_diagonal(self, geometry):
        assert geometry.distance([0, 0], [3, 4]) == pytest.approx(5.0)

    def test_calculate_area_square(self, geometry):
        points = [[0, 0], [4, 0], [4, 3], [0, 3]]
        result = geometry.calculate_area(points)
        assert result["area_m2"] == pytest.approx(12.0)
        assert result["perimeter_m"] == pytest.approx(14.0)

    def test_calculate_area_triangle(self, geometry):
        points = [[0, 0], [4, 0], [0, 3]]
        result = geometry.calculate_area(points)
        assert result["area_m2"] == pytest.approx(6.0)

    def test_calculate_area_too_few_points(self, geometry):
        result = geometry.calculate_area([[0, 0], [1, 1]])
        assert "error" in result

    def test_midpoint(self, geometry):
        mid = geometry.midpoint([0, 0], [4, 2])
        assert mid == [2.0, 1.0]

    def test_rectangle_points(self, geometry):
        pts = geometry.rectangle_points([1, 1], 3, 2)
        assert len(pts) == 4
        assert pts[0] == [1, 1]
        assert pts[2] == [4, 3]


# ─── CADSkills ───────────────────────────────────────────────────────────────

class TestCADSkills:
    def test_add_wall_returns_id(self, cad):
        result = cad.add_wall([0, 0], [5, 0])
        assert "id" in result
        assert result["id"].startswith("wall_")
        assert result["length_m"] == pytest.approx(5.0)
        assert result["status"] == "criada"

    def test_add_wall_stores_in_dict(self, cad):
        result = cad.add_wall([0, 0], [3, 0])
        assert result["id"] in cad.walls

    def test_add_door_valid_wall(self, cad):
        wall = cad.add_wall([0, 0], [5, 0])
        door = cad.add_door(wall["id"], 0.5, 0.90)
        assert door["status"] == "inserida"
        assert door["compliant"] is True

    def test_add_door_invalid_wall(self, cad):
        result = cad.add_door("wall_inexistente", 0.5, 0.90)
        assert "error" in result

    def test_add_door_narrow_not_compliant(self, cad):
        wall = cad.add_wall([0, 0], [5, 0])
        door = cad.add_door(wall["id"], 0.5, 0.70)
        assert door["compliant"] is False

    def test_add_window_valid(self, cad):
        wall = cad.add_wall([0, 0], [5, 0])
        win = cad.add_window(wall["id"], 0.5, 1.20, 1.20)
        assert win["status"] == "inserida"
        assert win["illumination_area_m2"] == pytest.approx(1.44)

    def test_add_dimension(self, cad):
        dim = cad.add_dimension([0, 0], [4, 0])
        assert dim["value_m"] == pytest.approx(4.0)

    def test_get_summary(self, cad):
        w = cad.add_wall([0, 0], [5, 0])
        cad.add_door(w["id"], 0.3, 0.90)
        cad.add_window(w["id"], 0.7, 1.20, 1.20)
        summary = cad.get_summary()
        assert summary["total_walls"] == 1
        assert summary["total_doors"] == 1
        assert summary["total_windows"] == 1


# ─── CarpentrySkills ─────────────────────────────────────────────────────────

class TestCarpentrySkills:
    def test_add_furniture_with_standard_size(self, carpentry):
        result = carpentry.add_furniture("cama_casal", [0, 0])
        assert result["status"] == "inserido"
        assert result["dimensions"]["width"] == pytest.approx(1.38)

    def test_add_furniture_custom_size(self, carpentry):
        result = carpentry.add_furniture("armario_cozinha_alto", [1, 0], width=0.80)
        assert result["dimensions"]["width"] == pytest.approx(0.80)

    def test_suggest_wood_economico_interno(self, carpentry):
        result = carpentry.suggest_wood("móvel", "economico", "interno")
        assert len(result["suggestions"]) > 0
        names = [s["wood"] for s in result["suggestions"]]
        assert any(w in names for w in ["MDF", "MDP", "pinus"])

    def test_suggest_wood_premium_externo(self, carpentry):
        result = carpentry.suggest_wood("deck", "premium", "externo")
        assert len(result["suggestions"]) > 0

    def test_calculate_materials_returns_area(self, carpentry):
        dims = {"width": 0.60, "height": 2.10, "depth": 0.35}
        result = carpentry.calculate_materials("armario_cozinha_alto", dims)
        assert result["total_area_m2"] > 0
        assert result["chapas_needed"] > 0


# ─── FloorPlanSkills ─────────────────────────────────────────────────────────

class TestFloorPlanSkills:
    def test_add_room_creates_4_walls(self, floor_plan):
        result = floor_plan.add_room("Sala", [0, 0], 4.0, 3.5)
        assert len(result["wall_ids"]) == 4
        assert result["area_m2"] == pytest.approx(14.0)

    def test_add_room_nbr_compliant_sala(self, floor_plan):
        result = floor_plan.add_room("Sala de Estar", [0, 0], 5.0, 4.0)
        assert result["nbr_compliance"]["compliant"] is True

    def test_add_room_nbr_non_compliant_sala(self, floor_plan):
        result = floor_plan.add_room("Sala", [0, 0], 2.0, 2.0)
        assert result["nbr_compliance"]["compliant"] is False
        assert len(result["nbr_compliance"]["issues"]) > 0

    def test_check_nbr_banheiro_ok(self, floor_plan):
        result = floor_plan.check_nbr_compliance("banheiro", 3.96, 1.80)
        assert result["compliant"] is True

    def test_check_nbr_banheiro_fail(self, floor_plan):
        result = floor_plan.check_nbr_compliance("banheiro", 2.0, 1.0)
        assert result["compliant"] is False

    def test_classify_room_quarto(self):
        assert FloorPlanSkills._classify_room("Quarto Casal") == "quarto_casal"
        assert FloorPlanSkills._classify_room("Suíte Master") == "quarto_casal"
        assert FloorPlanSkills._classify_room("Quarto Infantil") == "quarto_solteiro"
        assert FloorPlanSkills._classify_room("Banheiro Social") == "banheiro"
        assert FloorPlanSkills._classify_room("Cozinha") == "cozinha"
