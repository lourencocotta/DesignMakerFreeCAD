"""
Interface com o FreeCAD via subprocess ou importação direta.

Quando executado dentro do FreeCAD (com FreeCAD no PATH), usa a API nativa.
Fora do FreeCAD, simula as operações e gera scripts de macro (.FCMacro)
que podem ser abertos no FreeCAD manualmente.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path


def _freecad_available() -> bool:
    try:
        import FreeCAD  # noqa: F401
        return True
    except ImportError:
        return False


FREECAD_AVAILABLE = _freecad_available()


class FreeCadTools:
    """Gerencia operações no FreeCAD — nativo ou via geração de macros."""

    def __init__(self, freecad_path: str | None = None):
        self.freecad_path = freecad_path or os.environ.get("FREECAD_PATH", "FreeCAD")
        self.document_name: str | None = None
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self._macro_lines: list[str] = []
        self._objects: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------

    def create_document(self, name: str, scale: float = 0.01) -> dict:
        self.document_name = name
        self._macro_lines = [
            "import FreeCAD, Draft, Arch",
            "import FreeCADGui",
            f'doc = FreeCAD.newDocument("{name}")',
            f"# Scale: 1:{int(1/scale) if scale < 1 else scale}",
            "",
        ]
        return {
            "name": name,
            "scale": scale,
            "status": "documento_criado",
            "mode": "native" if FREECAD_AVAILABLE else "macro_generation",
        }

    def register_object(self, obj_type: str, obj_id: str, data: dict) -> None:
        self._objects[obj_id] = {"type": obj_type, **data}
        self._macro_lines.append(f"# {obj_type}: {obj_id} → {json.dumps(data)}")

    def export_drawing(
        self, format: str, output_path: str, scale: float = 0.01
    ) -> dict:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "dxf":
            return self._export_dxf(path)
        if format == "svg":
            return self._export_svg(path, scale)
        if format == "pdf":
            return self._export_pdf(path)

        return {"error": f"Formato '{format}' não suportado"}

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def _export_dxf(self, path: Path) -> dict:
        macro_path = self._save_macro(path.with_suffix(".FCMacro"))
        return {
            "format": "dxf",
            "output": str(path),
            "macro": str(macro_path),
            "status": "macro_gerada_para_exportacao",
            "instruction": f"Abra o FreeCAD e execute a macro: {macro_path}",
        }

    def _export_svg(self, path: Path, scale: float) -> dict:
        svg_content = self._generate_svg(scale)
        path.write_text(svg_content, encoding="utf-8")
        return {
            "format": "svg",
            "output": str(path),
            "objects_count": len(self._objects),
            "status": "exportado",
        }

    def _export_pdf(self, path: Path) -> dict:
        svg_path = path.with_suffix(".svg")
        self._export_svg(svg_path, 0.01)
        return {
            "format": "pdf",
            "svg_intermediate": str(svg_path),
            "output": str(path),
            "status": "svg_gerado_converter_com_inkscape",
            "instruction": f"Execute: inkscape {svg_path} --export-pdf={path}",
        }

    def _save_macro(self, path: Path) -> Path:
        path.write_text("\n".join(self._macro_lines), encoding="utf-8")
        return path

    def _generate_svg(self, scale: float = 0.01) -> str:
        m2px = 100  # 1 metro = 100px
        walls = [o for o in self._objects.values() if o.get("type") == "wall"]

        lines = []
        for w in walls:
            x1, y1 = w.get("start", [0, 0])
            x2, y2 = w.get("end", [0, 0])
            t = w.get("thickness", 0.15) * m2px
            lines.append(
                f'  <line x1="{x1*m2px}" y1="{y1*m2px}" '
                f'x2="{x2*m2px}" y2="{y2*m2px}" '
                f'stroke="black" stroke-width="{t}"/>'
            )

        svg = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">\n'
            f"  <!-- DesignMakerFreeCAD — Planta Baixa: {self.document_name} -->\n"
            + "\n".join(lines)
            + "\n</svg>"
        )
        return svg

    # ------------------------------------------------------------------
    # Macro runner (when FreeCAD is available on CLI)
    # ------------------------------------------------------------------

    def run_macro(self, macro_path: str) -> dict:
        if not FREECAD_AVAILABLE:
            cmd = [self.freecad_path, "--console", macro_path]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return {
                    "returncode": result.returncode,
                    "stdout": result.stdout[-2000:],
                    "stderr": result.stderr[-500:],
                }
            except FileNotFoundError:
                return {"error": "FreeCAD não encontrado. Defina FREECAD_PATH."}
            except subprocess.TimeoutExpired:
                return {"error": "Timeout ao executar macro"}
        else:
            import FreeCAD
            exec(open(macro_path).read(), {"FreeCAD": FreeCAD})  # noqa: S102
            return {"status": "macro_executada_nativamente"}
