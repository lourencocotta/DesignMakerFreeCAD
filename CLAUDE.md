# DesignMakerFreeCAD — CLAUDE.md

## Visão geral do projeto

Agente desenhista de plantas baixas em Python, com skills de CAD (FreeCAD) e carpintaria. O agente usa a API Claude para raciocinar sobre projetos arquitetônicos e delega ações a macros FreeCAD.

## Estrutura de diretórios

```
DesignMakerFreeCAD/
├── agent/                    # Núcleo do agente
│   ├── designer_agent.py     # DesignerAgent — loop agentico principal
│   ├── skills/
│   │   ├── cad_skills.py     # Paredes, portas, janelas, cotas
│   │   ├── carpentry_skills.py # Móveis, madeiras, cálculo de materiais
│   │   └── floor_plan_skills.py # Cômodos, verificação NBR
│   └── tools/
│       ├── freecad_tools.py  # Interface FreeCAD (nativo ou geração de macro)
│       └── geometry_tools.py # Geometria 2D (área, distância, bounding box)
├── macros/                   # Macros FreeCAD executáveis (.py / .FCMacro)
│   ├── floor_plan/
│   │   ├── create_room.py    # Cria cômodo retangular completo
│   │   ├── add_wall.py       # Adiciona parede individual
│   │   ├── add_door.py       # Insere porta em parede
│   │   ├── add_window.py     # Insere janela em parede
│   │   └── furniture/
│   │       └── carpentry_elements.py # Cria móveis 3D
│   └── utils/
│       ├── dimensions.py     # Cotas, labels, seta de Norte
│       └── standards.py      # Normas NBR (6492, 9050, 15575)
├── templates/
│   ├── rooms/                # Templates JSON por tipo de cômodo
│   └── furniture/            # Catálogo de móveis e madeiras
├── examples/                 # Scripts de uso end-to-end
└── tests/                    # Pytest — skills e macros
```

## Variáveis de ambiente obrigatórias

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API Claude |
| `FREECAD_PATH` | Caminho do executável FreeCAD (opcional, padrão: `FreeCAD`) |

## Comandos comuns

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar testes (não requer FreeCAD)
pytest tests/ -v

# Executar exemplos
python examples/simple_apartment.py
python examples/house_with_carpentry.py
```

## Modelo Claude em uso

`claude-sonnet-4-6` — definido em `agent/designer_agent.py:MODEL`.

## Normas implementadas

- **NBR 6492** — Escalas e representação de projetos
- **NBR 9050** — Acessibilidade (larguras mínimas de portas/corredores)
- **NBR 15575** — Dimensões mínimas de cômodos, iluminação e ventilação
- **NBR 10821** — Esquadrias (peitoril mínimo)

## Convenções de coordenadas

- Unidade: **metros** em toda a camada Python
- FreeCAD usa **milímetros** internamente — a conversão `mm(v) = v * 1000` é feita nas macros
- Origem `[0, 0]` = canto inferior-esquerdo da planta
- Eixo Y cresce para o Norte

## Como adicionar uma nova ferramenta ao agente

1. Implemente o método na skill adequada (`cad_skills.py`, `carpentry_skills.py` ou `floor_plan_skills.py`)
2. Registre no `_dispatch_tool` em `designer_agent.py`
3. Adicione o schema JSON em `_build_tools` em `designer_agent.py`
4. Escreva teste em `tests/test_agent.py`
