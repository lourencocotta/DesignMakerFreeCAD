"""
Exemplo: Casa com carpintaria planejada

Demonstra o agente criando uma casa térrea com ênfase em
móveis planejados e detalhamento de carpintaria.

Uso:
    export ANTHROPIC_API_KEY="sua-chave"
    python examples/house_with_carpentry.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.designer_agent import DesignerAgent


BRIEFING = """
Preciso do projeto de uma casa térrea com as seguintes especificações:

PROGRAMA:
- Suíte master com closet (mín. 12m²)
- 2 quartos solteiro (mín. 9m² cada)
- Sala de estar/jantar integrada (mín. 20m²)
- Cozinha americana (mín. 8m²)
- 2 banheiros (social + suíte)
- Área de serviço (mín. 4m²)
- Garagem para 1 carro (mín. 12m²)

CARPINTARIA:
- Cozinha planejada completa (armários altos + baixos + ilha)
- Guarda-roupas planejados em todos os quartos
- Closet na suíte com ilhota central
- Bancada no banheiro da suíte em MDF com mármore

RESTRIÇÕES:
- Terreno 10x20m (frente sul)
- Recuos: 2m frente, 1.5m fundos, 1.5m laterais
- Área construída máxima: ~120m²
- Pé-direito 2.80m
"""


def main():
    agent = DesignerAgent()

    print("=" * 70)
    print("DesignMakerFreeCAD — Exemplo: Casa com Carpintaria Planejada")
    print("=" * 70)

    # Passo 1 — Briefing completo
    print("\n[1] Enviando briefing do projeto...")
    r1 = agent.chat(BRIEFING)
    print(f"AGENTE:\n{r1}\n")

    # Passo 2 — Detalhamento da carpintaria da cozinha
    print("\n[2] Detalhando carpintaria da cozinha...")
    r2 = agent.chat(
        "Detalhe os armários da cozinha: quais dimensões, materiais e encaixes "
        "você recomenda? Calcule a quantidade de chapas de MDF necessárias."
    )
    print(f"AGENTE:\n{r2}\n")

    # Passo 3 — Verificação de normas
    print("\n[3] Verificando conformidade NBR...")
    r3 = agent.chat(
        "Verifique se todos os cômodos atendem NBR 15575 e NBR 9050. "
        "Liste qualquer problema encontrado."
    )
    print(f"AGENTE:\n{r3}\n")

    # Passo 4 — Exportação
    print("\n[4] Exportando projeto...")
    r4 = agent.chat(
        "Exporte a planta baixa em SVG em output/casa_carpintaria.svg "
        "e gere também a macro FreeCAD em output/casa_carpintaria.FCMacro."
    )
    print(f"AGENTE:\n{r4}\n")


if __name__ == "__main__":
    main()
