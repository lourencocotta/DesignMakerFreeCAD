"""
Exemplo: Apartamento simples de 2 quartos

Demonstra o uso do DesignerAgent para criar uma planta baixa completa
via conversa em linguagem natural.

Uso:
    export ANTHROPIC_API_KEY="sua-chave"
    python examples/simple_apartment.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.designer_agent import DesignerAgent


def main():
    agent = DesignerAgent()

    print("=" * 60)
    print("DesignMakerFreeCAD — Exemplo: Apartamento 2 Quartos")
    print("=" * 60)

    # Sessão de conversa
    messages = [
        (
            "Olá! Quero criar a planta baixa de um apartamento de 2 quartos. "
            "A área total é de aproximadamente 60m². "
            "Preciso de: sala, cozinha americana, 2 quartos, 1 banheiro social e área de serviço. "
            "Pode começar o projeto?"
        ),
        (
            "O apartamento tem formato retangular, com 8m de frente por 8m de profundidade. "
            "A entrada principal fica na parede sul (y=0). "
            "Pode criar o layout completo com os cômodos?"
        ),
        (
            "Agora adicione os móveis principais: "
            "cama de casal no quarto maior, cama de solteiro no menor, "
            "sofá de 3 lugares na sala e a cozinha planejada com armários em L."
        ),
        (
            "Quais madeiras você recomenda para os armários da cozinha e o guarda-roupa? "
            "Orçamento médio, ambiente interno."
        ),
        (
            "Perfeito! Verifique se todos os cômodos estão em conformidade com a NBR "
            "e exporte a planta em SVG."
        ),
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n[{i}] USUÁRIO: {msg[:80]}{'...' if len(msg) > 80 else ''}")
        print("-" * 60)
        response = agent.chat(msg)
        print(f"AGENTE: {response}")
        print()


if __name__ == "__main__":
    main()
