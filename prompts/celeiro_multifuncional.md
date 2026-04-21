# Prompt — Planta Baixa: Celeiro Multifuncional Rural

Gere uma macro Python completa para FreeCAD que desenhe a planta baixa
do celeiro conforme especificações abaixo. Use o módulo `Arch` do FreeCAD
(`ArchWall`, `ArchDoor`, `ArchWindow`) e a convenção de unidades em milímetros
internamente. Todas as cotas do memorial estão em metros; converta com `mm(v) = v * 1000`.

---

## Sistema de Coordenadas

- Origem `[0, 0]` = canto inferior-esquerdo (fachada frontal / portão)
- Eixo X → cresce para a direita (leste)
- Eixo Y → cresce para o fundo / norte
- Espessura padrão das paredes: **0,20 m** (alvenaria tijolo cerâmico)

---

## Envelope Geral do Edifício

Planta retangular: largura **8,50 m** (X) × profundidade **10,00 m** (Y) = **85,00 m²**

Paredes perimetrais (todas espessura 0,20 m, altura 3,50 m):

| Parede | De (mm) | Até (mm) | Comprimento |
|---|---|---|---|
| Frontal (sul) | `[0, 0]` | `[8500, 0]` | 8500 mm |
| Lateral (leste) | `[8500, 0]` | `[8500, 10000]` | 10000 mm |
| Fundo (norte) | `[0, 10000]` | `[8500, 10000]` | 8500 mm |
| Lateral (oeste) | `[0, 0]` | `[0, 10000]` | 10000 mm |

---

## Setorização Interna — Bloco de Serviços (fundo, Y = 7500 a 10000)

**Parede transversal de divisão** (bloco serviços × galpão):
- De `[0, 7500]` → `[8500, 7500]`, espessura 0,20 m, altura 2,20 m
- (altura da laje do bloco de serviços = 2,20 m)

### 2.1 Cômodo Principal

- Posição: canto inferior-esquerdo `[0, 7500]`, largura 6000 mm, profundidade 2500 mm
- Paredes internas (espessura 0,15 m, altura 2,20 m):
  - Parede divisória direita: `[6000, 7500]` → `[6000, 10000]`
- **Porta de acesso pelo galpão:** largura 0,90 m × altura 2,10 m
  - Posição: parede transversal Y=7500, centrada em X=3000
- **Janela lateral oeste:** 1,00 × 1,20 m (L × H), peitoril 0,90 m
  - Posição: parede oeste X=0, centrada em Y=8750

### 2.2 Escada de Acesso ao Mezanino

Representar como retângulo hachurado na planta:
- Posição: `[200, 7700]` → `[1000, 9500]` (1,00 × 1,80 m, junto à parede oeste)
- Label: `"ESC. MEZANINO 0,90m"`

### 2.3 Área Aberta com Pia

- Limites: X=6200 a 8500, Y=7500 a 8800 (área ≈ 2,30 × 1,30 m)
- Sem paredes internas — espaço integrado ao galpão
- **Pia (lavatório):** símbolo 600 × 500 mm, encostada na parede do fundo (Y=10000), centrada em X=7250

### 2.4 Banheiro (box de chuveiro)

- Posição: `[7300, 8800]` → `[8500, 10000]` (1,20 × 1,20 m)
- Paredes internas (espessura 0,10 m, altura 2,20 m):
  - Parede esquerda: `[7300, 8800]` → `[7300, 10000]`
  - Parede frontal: `[7300, 8800]` → `[8500, 8800]`
- **Porta:** 0,80 m, abrindo para fora (área aberta), junto à parede direita
- **Janela exterior** (parede leste X=8500): 0,40 × 0,60 m, peitoril 1,20 m, basculante, centrada em Y=9400

### 2.5 W.C. (vaso sanitário)

- Posição: `[6200, 8800]` → `[7300, 10000]` (1,10 × 1,20 m)
- Paredes internas (espessura 0,10 m, altura 2,20 m):
  - Parede esquerda: `[6200, 8800]` → `[6200, 10000]`
  - Parede frontal: `[6200, 8800]` → `[7300, 8800]`
- **Porta:** 0,80 m, abrindo para fora (área aberta), lado esquerdo
- **Janela exterior** (parede leste X=8500): 0,40 × 0,60 m, peitoril 1,20 m, basculante, centrada em Y=9400

---

## Área Principal do Galpão (Y = 0 a 7500, ~53 m²)

Espaço totalmente livre — sem paredes internas.
Pé-direito: 3,50 m nas laterais / 5,00 m na cumeeira (representar em corte, não na planta).

### Portão principal (fachada frontal sul, Y=0)

- Tipo: portão basculante ou de correr, **4,00 × 3,20 m** (L × H)
- Posição: centralizado, X = 2250 a 6250 mm

### Porta lateral de serviço (parede oeste, X=0)

- Tipo: porta simples, **1,00 × 2,10 m** (L × H)
- Posição: parede oeste X=0, Y=3500

### Janelas laterais — ventilação cruzada

**Parede leste (X=8500)** — 2 janelas venezianas:

| ID | Centro Y | Dimensão (mm) | Peitoril |
|---|---|---|---|
| L1 | 1800 | 2000 × 1400 | 1200 mm |
| L2 | 5500 | 2000 × 1400 | 1200 mm |

**Parede oeste (X=0)** — 2 janelas venezianas + 1 menor:

| ID | Centro Y | Dimensão (mm) | Peitoril |
|---|---|---|---|
| O1 | 1800 | 2000 × 1400 | 1200 mm |
| O2 | 5500 | 2000 × 1400 | 1200 mm |
| O3 | 6800 | 1000 × 1400 | 1200 mm |

---

## Zona de Abate

Representar como área hachurada no canto nordeste do galpão:
- Limites: `[5500, 6000]` → `[8300, 7500]` (≈ 2,80 × 1,50 m)
- Label: `"ZONA DE ABATE"`
- Canaleta central: 200 mm de largura, Y=6750, de X=5500 a 8300
- Label canaleta: `"CANALETA c/ GRELHA 200mm"`

---

## Mobiliário / Equipamentos (representação esquemática)

| Elemento | Símbolo | Posição (mm) |
|---|---|---|
| Bancada de carpintaria | Retângulo 3000 × 600 | `[200, 200]` → `[3200, 800]` |
| Pia (área aberta) | Retângulo 600 × 500 | centro `[7250, 9800]` |
| Vaso sanitário (WC) | Retângulo 400 × 650 | centro `[6600, 9600]` |
| Chuveiro (banheiro) | Círculo ø 900 | centro `[7900, 9400]` |

---

## Cotas e Anotações

Gerar cotas lineares (`Draft.makeDimension`) para:

1. Largura total: 8,50 m — cota externa, Y = −1000 mm
2. Profundidade total: 10,00 m — cota externa, X = 9700 mm
3. Cômodo principal: 6,00 m × 2,50 m (cotas internas)
4. Bloco de serviços: profundidade 2,50 m (cota externa fundo)
5. Portão: 4,00 m (cota sobre o vão)
6. Porta de serviço: 1,00 m (cota sobre o vão)
7. Banheiro: 1,20 × 1,20 m
8. WC: 1,20 × 1,20 m

Labels de ambientes (`Draft.makeText`):

| Label | Posição (mm) |
|---|---|
| `"GALPÃO PRINCIPAL\n~53,00 m²"` | `[4250, 3750]` |
| `"CÔMODO\n15,00 m²"` | `[3000, 8750]` |
| `"MEZANINO\n(sobre o cômodo)\n15,00 m²"` | `[3000, 9300]` |
| `"ÁREA ABERTA\nC/ PIA"` | `[7350, 8200]` |
| `"BANHEIRO\n1,44 m²"` | `[7900, 9300]` |
| `"W.C.\n1,44 m²"` | `[6750, 9300]` |
| `"ZONA DE ABATE"` | `[6900, 6750]` |
| `"BANCADA CARPINTARIA"` | `[1700, 500]` |

Seta de Norte apontando para Y+, posição `[9200, 9500]`.

---

## Estrutura da Macro

Organizar em funções:

```python
import FreeCAD, FreeCADGui, Draft, Arch

doc = FreeCAD.newDocument("Celeiro_Multifuncional")
mm = lambda v: v * 1000  # metros → mm

def create_envelope(): ...       # paredes perimetrais
def create_service_block(): ...  # cômodo, banheiro, WC, área aberta
def add_openings(): ...          # portão, portas, janelas (ArchDoor / ArchWindow)
def add_slaughter_zone(): ...    # demarcação zona de abate + canaleta
def add_furniture_symbols(): ... # Draft.makeRectangle / makeCircle
def add_dimensions_labels(): ... # Draft.makeDimension / makeText

def main():
    create_envelope()
    create_service_block()
    add_openings()
    add_slaughter_zone()
    add_furniture_symbols()
    add_dimensions_labels()
    doc.recompute()
    FreeCADGui.activeDocument().activeView().viewTop()
    FreeCADGui.SendMsgToActiveView("ViewFit")

main()
```

---

## Restrições e Normas

| Norma | Requisito | Status |
|---|---|---|
| NBR 9050 | Vãos mínimos de porta ≥ 0,80 m | ✓ |
| NBR 9077 | Guarda-corpo mezanino ≥ 1,10 m | Anotar em label |
| — | Portão ≥ 3,20 m altura (caminhão MB-608) | ✓ |
| — | Janelas sanitários voltadas para exterior (leste) | ✓ |
| — | Escada: largura útil 0,90 m, 13 degraus, desnível 2,20 m | ✓ |
