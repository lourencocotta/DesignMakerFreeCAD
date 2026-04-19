"""
DesignerAgent — agente desenhista de plantas baixas com skills de CAD (FreeCAD) e carpintaria.

Utiliza a API Claude para raciocinar sobre o projeto e delegar ações às ferramentas
FreeCAD via macros Python.
"""

import json
import os
from typing import Any

import anthropic

from .skills.cad_skills import CADSkills
from .skills.carpentry_skills import CarpentrySkills
from .skills.floor_plan_skills import FloorPlanSkills
from .tools.freecad_tools import FreeCadTools
from .tools.geometry_tools import GeometryTools

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Você é um desenhista técnico especializado em plantas baixas residenciais e
comerciais, com profundo conhecimento em:

1. **CAD / FreeCAD**: criação de elementos arquitetônicos (paredes, portas, janelas, escadas),
   cotas, hachuras, layers e exportação para DXF/SVG/PDF.
2. **Carpintaria**: móveis planejados, armários embutidos, bancadas, detalhamento de
   junções, encaixes (cavilha, rabo-de-andorinha, espiga), acabamentos e madeiras comuns
   no mercado brasileiro.
3. **Normas brasileiras**: NBR 6492 (representação de projetos de arquitetura), NBR 9050
   (acessibilidade), NBR 15575 (desempenho de edificações) e posturas municipais típicas.

Ao receber uma solicitação de projeto:
- Faça perguntas de clarificação quando necessário (área, programa de necessidades,
  estilo, restrições).
- Planeje o desenho passo a passo antes de chamar ferramentas.
- Use as ferramentas disponíveis para criar o projeto no FreeCAD.
- Documente cada decisão de projeto com justificativa técnica.
- Sempre verifique se as dimensões respeitam as normas vigentes.

Responda sempre em português brasileiro."""


class DesignerAgent:
    """Agente desenhista que usa Claude + ferramentas FreeCAD para criar plantas baixas."""

    def __init__(self, api_key: str | None = None, freecad_path: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.freecad = FreeCadTools(freecad_path=freecad_path)
        self.geometry = GeometryTools()
        self.cad = CADSkills(self.freecad, self.geometry)
        self.carpentry = CarpentrySkills()
        self.floor_plan = FloorPlanSkills(self.cad, self.carpentry)
        self.conversation: list[dict[str, Any]] = []
        self._tools = self._build_tools()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """Envia uma mensagem ao agente e retorna a resposta."""
        self.conversation.append({"role": "user", "content": user_message})
        response_text = self._run_agent_loop()
        self.conversation.append({"role": "assistant", "content": response_text})
        return response_text

    def reset(self) -> None:
        """Limpa o histórico da conversa."""
        self.conversation.clear()

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _run_agent_loop(self) -> str:
        """Executa o loop agentico: Claude → tool calls → Claude → …"""
        messages = list(self.conversation)

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=8096,
                system=SYSTEM_PROMPT,
                tools=self._tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            if response.stop_reason == "tool_use":
                tool_results = self._execute_tool_calls(response)
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                return self._extract_text(response)

    def _execute_tool_calls(self, response) -> list[dict]:
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            output = self._dispatch_tool(block.name, block.input)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output, ensure_ascii=False),
                }
            )
        return results

    def _dispatch_tool(self, name: str, args: dict) -> Any:
        dispatch = {
            # CAD / FreeCAD
            "create_document": self.freecad.create_document,
            "add_wall": self.cad.add_wall,
            "add_door": self.cad.add_door,
            "add_window": self.cad.add_window,
            "add_room": self.floor_plan.add_room,
            "add_dimension": self.cad.add_dimension,
            "export_drawing": self.freecad.export_drawing,
            # Carpintaria
            "add_furniture": self.carpentry.add_furniture,
            "suggest_wood": self.carpentry.suggest_wood,
            "calculate_materials": self.carpentry.calculate_materials,
            # Geometria
            "calculate_area": self.geometry.calculate_area,
            "check_nbr_compliance": self.floor_plan.check_nbr_compliance,
        }
        handler = dispatch.get(name)
        if handler is None:
            return {"error": f"Ferramenta desconhecida: {name}"}
        try:
            return handler(**args)
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def _extract_text(response) -> str:
        parts = [b.text for b in response.content if hasattr(b, "text")]
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Tool schemas
    # ------------------------------------------------------------------

    def _build_tools(self) -> list[dict]:
        return [
            {
                "name": "create_document",
                "description": "Cria um novo documento FreeCAD para a planta baixa.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do documento/projeto"},
                        "scale": {"type": "number", "description": "Escala (ex: 0.01 para 1:100)"},
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "add_wall",
                "description": "Adiciona uma parede à planta baixa.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Ponto inicial [x, y] em metros",
                        },
                        "end": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Ponto final [x, y] em metros",
                        },
                        "thickness": {
                            "type": "number",
                            "description": "Espessura da parede em metros (padrão 0.15)",
                        },
                        "height": {
                            "type": "number",
                            "description": "Altura da parede em metros (padrão 2.80)",
                        },
                        "material": {
                            "type": "string",
                            "description": "Material: alvenaria, drywall, concreto",
                        },
                    },
                    "required": ["start", "end"],
                },
            },
            {
                "name": "add_door",
                "description": "Adiciona uma porta em uma parede.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wall_id": {"type": "string", "description": "ID da parede"},
                        "position": {
                            "type": "number",
                            "description": "Posição ao longo da parede (0.0 a 1.0)",
                        },
                        "width": {"type": "number", "description": "Largura da porta em metros"},
                        "height": {"type": "number", "description": "Altura da porta em metros"},
                        "opening_side": {
                            "type": "string",
                            "enum": ["left", "right"],
                            "description": "Sentido de abertura",
                        },
                        "door_type": {
                            "type": "string",
                            "enum": ["simples", "dupla", "correr", "pivotante"],
                        },
                    },
                    "required": ["wall_id", "position", "width"],
                },
            },
            {
                "name": "add_window",
                "description": "Adiciona uma janela em uma parede.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wall_id": {"type": "string", "description": "ID da parede"},
                        "position": {"type": "number", "description": "Posição (0.0 a 1.0)"},
                        "width": {"type": "number", "description": "Largura em metros"},
                        "height": {"type": "number", "description": "Altura em metros"},
                        "sill_height": {
                            "type": "number",
                            "description": "Peitoril em metros (padrão 0.90)",
                        },
                        "window_type": {
                            "type": "string",
                            "enum": ["maxim-ar", "correr", "guilhotina", "basculante", "fixa"],
                        },
                    },
                    "required": ["wall_id", "position", "width", "height"],
                },
            },
            {
                "name": "add_room",
                "description": "Adiciona um cômodo completo (paredes + identificação) à planta.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do cômodo"},
                        "origin": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Canto inferior-esquerdo [x, y] em metros",
                        },
                        "width": {"type": "number", "description": "Largura em metros"},
                        "depth": {"type": "number", "description": "Profundidade em metros"},
                        "wall_thickness": {"type": "number", "description": "Espessura das paredes"},
                    },
                    "required": ["name", "origin", "width", "depth"],
                },
            },
            {
                "name": "add_dimension",
                "description": "Adiciona cota/dimensão ao desenho.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "array", "items": {"type": "number"}},
                        "end": {"type": "array", "items": {"type": "number"}},
                        "offset": {
                            "type": "number",
                            "description": "Distância da linha de cota ao elemento",
                        },
                    },
                    "required": ["start", "end"],
                },
            },
            {
                "name": "add_furniture",
                "description": "Adiciona elemento de carpintaria/móvel à planta.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "furniture_type": {
                            "type": "string",
                            "description": "Tipo: armario, bancada, cama, mesa, sofa, etc.",
                        },
                        "position": {"type": "array", "items": {"type": "number"}},
                        "width": {"type": "number"},
                        "depth": {"type": "number"},
                        "height": {"type": "number"},
                        "rotation": {"type": "number", "description": "Rotação em graus"},
                        "material": {"type": "string", "description": "Material/madeira"},
                    },
                    "required": ["furniture_type", "position", "width", "depth"],
                },
            },
            {
                "name": "suggest_wood",
                "description": "Sugere tipo de madeira para aplicação específica.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "application": {
                            "type": "string",
                            "description": "Aplicação: estrutural, móvel, revestimento, etc.",
                        },
                        "budget": {
                            "type": "string",
                            "enum": ["economico", "medio", "premium"],
                        },
                        "environment": {
                            "type": "string",
                            "enum": ["interno", "externo", "umido"],
                        },
                    },
                    "required": ["application"],
                },
            },
            {
                "name": "calculate_materials",
                "description": "Calcula quantidade de materiais para carpintaria.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "furniture_type": {"type": "string"},
                        "dimensions": {
                            "type": "object",
                            "properties": {
                                "width": {"type": "number"},
                                "height": {"type": "number"},
                                "depth": {"type": "number"},
                            },
                        },
                        "material": {"type": "string"},
                    },
                    "required": ["furniture_type", "dimensions"],
                },
            },
            {
                "name": "calculate_area",
                "description": "Calcula a área de um polígono.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "points": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "number"}},
                            "description": "Lista de pontos [[x1,y1], [x2,y2], ...]",
                        }
                    },
                    "required": ["points"],
                },
            },
            {
                "name": "check_nbr_compliance",
                "description": "Verifica conformidade com normas NBR para o cômodo.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "room_type": {
                            "type": "string",
                            "description": "Tipo de cômodo: quarto, sala, banheiro, cozinha, etc.",
                        },
                        "area": {"type": "number", "description": "Área em m²"},
                        "width": {"type": "number", "description": "Menor dimensão em metros"},
                    },
                    "required": ["room_type", "area"],
                },
            },
            {
                "name": "export_drawing",
                "description": "Exporta o desenho para DXF, SVG ou PDF.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["dxf", "svg", "pdf"],
                        },
                        "output_path": {"type": "string"},
                        "scale": {"type": "number"},
                    },
                    "required": ["format", "output_path"],
                },
            },
        ]
