"""Utilitários de geometria 2D para plantas baixas."""

from __future__ import annotations

import math


class GeometryTools:
    """Operações geométricas básicas para projetos de planta baixa."""

    @staticmethod
    def distance(p1: list[float], p2: list[float]) -> float:
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    @staticmethod
    def calculate_area(points: list[list[float]]) -> dict:
        """Shoelace formula para área de polígono."""
        n = len(points)
        if n < 3:
            return {"error": "Mínimo de 3 pontos necessários", "area_m2": 0}

        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        area = abs(area) / 2.0

        perimeter = sum(
            GeometryTools.distance(points[i], points[(i + 1) % n]) for i in range(n)
        )

        return {
            "area_m2": round(area, 3),
            "perimeter_m": round(perimeter, 3),
            "points_count": n,
        }

    @staticmethod
    def midpoint(p1: list[float], p2: list[float]) -> list[float]:
        return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

    @staticmethod
    def angle_degrees(p1: list[float], p2: list[float]) -> float:
        return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

    @staticmethod
    def offset_point(
        p1: list[float], p2: list[float], offset: float
    ) -> tuple[list[float], list[float]]:
        """Retorna par de pontos deslocados perpendicularmente (para linhas de cota)."""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx * dx + dy * dy) or 1
        nx, ny = -dy / length, dx / length
        return (
            [p1[0] + nx * offset, p1[1] + ny * offset],
            [p2[0] + nx * offset, p2[1] + ny * offset],
        )

    @staticmethod
    def rectangle_points(
        origin: list[float], width: float, depth: float
    ) -> list[list[float]]:
        x, y = origin
        return [[x, y], [x + width, y], [x + width, y + depth], [x, y + depth]]

    @staticmethod
    def bounding_box(points: list[list[float]]) -> dict:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return {
            "min_x": min(xs),
            "min_y": min(ys),
            "max_x": max(xs),
            "max_y": max(ys),
            "width": max(xs) - min(xs),
            "height": max(ys) - min(ys),
        }
