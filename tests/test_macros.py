"""Testes das macros utilitárias (sem FreeCAD — testa lógica pura)."""

import pytest
from macros.utils.standards import (
    check_room,
    required_window_area,
    check_accessibility,
    ROOM_MINIMUMS,
    ACCESSIBILITY,
)


class TestNBRStandards:
    def test_check_room_quarto_casal_ok(self):
        result = check_room("quarto_casal", 10.0, 3.0)
        assert result["compliant"] is True
        assert len(result["issues"]) == 0

    def test_check_room_quarto_casal_area_fail(self):
        result = check_room("quarto_casal", 8.0, 2.6)
        assert result["compliant"] is False
        assert any("Área" in i for i in result["issues"])

    def test_check_room_quarto_casal_width_fail(self):
        result = check_room("quarto_casal", 10.0, 2.0)
        assert result["compliant"] is False
        assert any("Largura" in i for i in result["issues"])

    def test_check_room_unknown_type(self):
        result = check_room("deposito", 5.0, 2.0)
        assert result["status"] == "norma_nao_mapeada"

    def test_required_window_area_sala(self):
        result = required_window_area(11.0, "sala")
        assert result["min_illumination_area_m2"] == pytest.approx(11.0 * 0.125, rel=1e-3)
        assert result["min_ventilation_area_m2"] == pytest.approx(11.0 * 0.08, rel=1e-3)

    def test_accessibility_door_ok(self):
        result = check_accessibility(0.90, 1.20)
        assert result["compliant"] is True
        assert result["accessible_door"] is True

    def test_accessibility_door_narrow(self):
        result = check_accessibility(0.70)
        assert result["compliant"] is False
        assert any("Porta" in i for i in result["issues"])

    def test_accessibility_corridor_narrow(self):
        result = check_accessibility(0.90, 0.80)
        assert result["compliant"] is False
        assert any("Corredor" in i for i in result["issues"])

    def test_all_rooms_have_required_keys(self):
        required_keys = {"area_m2", "min_width_m", "pe_direito_m"}
        for room_type, mins in ROOM_MINIMUMS.items():
            assert required_keys.issubset(mins.keys()), (
                f"Cômodo '{room_type}' falta chaves: {required_keys - mins.keys()}"
            )
