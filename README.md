# DesignMakerFreeCAD

Agente desenhista de **plantas baixas** baseado em macros Python para FreeCAD, com skills de **CAD** e **carpintaria**. Usa a API Claude para interpretar briefs em linguagem natural e gerar projetos arquitetônicos conformes às normas brasileiras.

---

## Funcionalidades

| Categoria | Capacidades |
|---|---|
| **Plantas baixas** | Criação de cômodos, paredes, portas, janelas, cotas |
| **Normas NBR** | Verificação automática de NBR 6492, 9050, 15575, 10821 |
| **Carpintaria** | Catálogo de móveis, cálculo de materiais, recomendação de madeiras |
| **Exportação** | SVG direto, macro `.FCMacro` para FreeCAD, PDF via Inkscape |
| **Conversação** | Diálogo em português via API Claude |

---

## Pré-requisitos

- Python 3.11+
- [FreeCAD 0.21+](https://www.freecad.org/downloads.php) (opcional — para execução nativa das macros)
- Chave de API Anthropic

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Uso rápido

```python
from agent.designer_agent import DesignerAgent

agent = DesignerAgent()

# Conversa em linguagem natural
r = agent.chat(
    "Crie a planta de um apartamento de 2 quartos, 60m², "
    "sala integrada com cozinha americana, 1 banheiro e área de serviço."
)
print(r)

# Adicionar carpintaria
r = agent.chat(
    "Adicione guarda-roupas planejados nos dois quartos em MDF. "
    "Qual madeira recomenda para a bancada da cozinha?"
)
print(r)

# Exportar
r = agent.chat("Exporte a planta em SVG em output/apartamento.svg")
print(r)
```

---

## Arquitetura do agente

```
Usuário (linguagem natural)
        │
        ▼
  DesignerAgent          ← loop agentico (Claude Sonnet)
        │
   ┌────┴────────────────────────────┐
   │                                 │
CADSkills                   CarpentrySkills
(paredes, portas,           (móveis, madeiras,
 janelas, cotas)             cálculo de chapas)
   │                                 │
   └──────────┬──────────────────────┘
              │
        FloorPlanSkills
        (cômodos, NBR)
              │
       ┌──────┴──────┐
  FreeCadTools   GeometryTools
  (FreeCAD API   (área, distância,
   ou macro)      bounding box)
```

---

## Macros FreeCAD

As macros em `macros/` podem ser executadas **diretamente no FreeCAD**:

1. Abra o FreeCAD
2. Menu **Macro → Macros...**
3. Selecione o arquivo `.py` desejado
4. Ajuste os parâmetros no topo do arquivo
5. Clique em **Executar**

### Macros disponíveis

| Arquivo | Função |
|---|---|
| `macros/floor_plan/create_room.py` | Cômodo retangular completo |
| `macros/floor_plan/add_wall.py` | Parede individual |
| `macros/floor_plan/add_door.py` | Porta em parede existente |
| `macros/floor_plan/add_window.py` | Janela em parede existente |
| `macros/floor_plan/furniture/carpentry_elements.py` | Móveis 3D |
| `macros/utils/dimensions.py` | Cotas e labels |
| `macros/utils/standards.py` | Verificação de normas NBR |

---

## Testes

```bash
pytest tests/ -v
```

Os testes não requerem FreeCAD instalado — testam a lógica Python pura das skills.

---

## Templates

### Cômodos (`templates/rooms/`)

- `bedroom.json` — Quarto de casal com layout de móveis
- `bathroom.json` — Banheiro social com fixtures sanitários
- `kitchen.json` — Cozinha americana com opções de layout (linear, paralelo, U)

### Mobiliário (`templates/furniture/`)

- `standard_sizes.json` — Dimensões padrão de +40 tipos de móveis
- `carpentry_catalog.json` — Catálogo de madeiras e painéis (MDF, MDP, compensado, ipê, cedro, etc.)

---

## Normas Brasileiras Implementadas

| Norma | Tema | Aplicação |
|---|---|---|
| NBR 6492:1994 | Representação de projetos | Escalas, convenções gráficas |
| NBR 9050:2020 | Acessibilidade | Largura mínima de portas e corredores |
| NBR 15575:2021 | Desempenho de edificações | Área mínima de cômodos, iluminação, ventilação |
| NBR 10821:2017 | Esquadrias | Peitoril mínimo (0,90m residencial) |

---

## Exemplos

```bash
# Apartamento simples 2 quartos
python examples/simple_apartment.py

# Casa com carpintaria planejada completa
python examples/house_with_carpentry.py
```

---

## Contribuindo

1. Crie sua branch a partir de `main`
2. Implemente a skill/macro
3. Adicione testes em `tests/`
4. Verifique normas NBR aplicáveis
5. Abra um Pull Request

---

## Licença

MIT
