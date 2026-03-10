# System 4 — Configuração da Simulação de Canal Adjacente

## Visão Geral

Este estudo avalia a interferência de canal adjacente causada pelo sistema **MSS DC (Direct-to-Client) System 4** operando na faixa **2110–2200 MHz** sobre receptores MSS terrestres (Earth Stations). A simulação é baseada nos documentos **WP4C-Working-Document-4C-528 (Annex 1)** e **4C/356-E (6 May 2025)**.

- **Interferidor**: MSS DC (Sistema 4) — enlace de descida (Downlink)
- **Vítimas**: Earth Stations MSS receptoras na faixa 2100 MHz
- **Tipo de estudo**: Canal adjacente — co-canal desabilitado
- **Referência geográfica**: Cidade de Assunção, Paraguai (25,2637° S, 57,5759° O)

---

## 1. Cenário de Interferência por Canal Adjacente

Utilizamos **primeira e segunda adjacências** de interferência. A frequência de recepção das Earth Stations é deslocada abaixo do limite inferior da banda do MSS DC (2162,5 MHz):

| Adjacência | Frequência da ES (MHz) | Deslocamento (offset) | ACLR aplicado |
|:---:|:---:|:---:|:---:|
| **1ª adjacência** | 2157,5 | −5 MHz | 45 dB |
| **2ª adjacência** | 2152,5 | −10 MHz | 50 dB |

O MSS DC transmite centrado em **2162,5 MHz** (limite inferior da banda DC-MSS). As emissões de canal adjacente são modeladas por **ACLR** (`adjacent_ch_emissions = ACLR`). A recepção de canal adjacente na ES está desabilitada (`adjacent_ch_reception = OFF`).

---

## 2. Sistema MSS DC — Interferidor (System 4, 690 km)

Referência: `imt.2110-2200MHz.mss-dc.system4-690km`

### 2.1 Parâmetros Orbitais

| Parâmetro | Valor |
|---|---|
| Número de planos | 96 |
| Inclinação | 53,0° |
| Altitude (perigeu/apogeu) | 690 km (órbita circular) |
| Satélites por plano | 1 |
| Long. do nó ascendente inicial | 1,875° |
| Fasagem | 97,5° |

### 2.2 Parâmetros do Transmissor (Satélite — BS)

| Parâmetro | Valor |
|---|---|
| Frequência central IMT | 2162,5 MHz |
| Largura de banda | 5 MHz |
| Potência conduzida (por elemento) | 33,39 dBm |
| Perda ôhmica | 0 dB |
| Figura de ruído | 5 dB |
| ACLR — 1ª adjacência | **45 dB** |
| ACLR — 2ª adjacência | **50 dB** |
| Probabilidade de carga simulada | 20% e 50% |

### 2.3 Padrão de Antena — System 4 (ITU-R S.1528)

O padrão de antena é o **Antenna System 4**, com dois conjuntos de parâmetros dependentes do ângulo de elevação do satélite:

| Região | Ganho máx. (dBi) | BW a −3 dB | Nível de lóbulo lateral (Ls) | Far-out sidelobe |
|---|:---:|:---:|:---:|:---:|
| Alta elevação (nadir) | 41,0 | 1,5° | −35 dB | −20 dB |
| Baixa elevação (borda de serviço) | 46,0 | 0,82° | −20 dB | −10 dB |

### 2.4 Topologia do Feixe

| Parâmetro | Valor |
|---|---|
| Raio do feixe | 24 km |
| Tipo de posicionamento | SERVICE\_GRID (grade aleatória por snapshot) |
| Área de serviço | Círculo de 1000 km centrado em Assunção |
| Ângulo mínimo de serviço | 32° |
| Condição de satélite ativo | Elevação mínima de 23,5° a partir da ES |
| Margem dos satélites elegíveis | −200 km da borda da grade |

---

## 3. Earth Stations MSS — Vítimas

Três tipos de receptores MSS são avaliados como vítimas. Todos operam com antena omnidirecional e apontamento aleatório.

Referência: Documento **4C/356-E**, Tabelas 7.1.4 e 7.1.5.

### 3.1 System R — Forward Link (7.1.4)

| Parâmetro | Valor |
|---|---|
| ID | `mss.2100MHz.7.1.4-forward-R` |
| Ganho de antena | 6,36 dBi |
| Largura de banda | 1,25 MHz |
| Temperatura de ruído | 273 K |
| Seletividade de canal adjacente (ACS) | 20 dB |
| Elevação mínima de operação | 10° |

### 3.2 ES Tipo 1 (7.1.5)

| Parâmetro | Valor |
|---|---|
| ID | `mss.2100MHz.7.1.5-ES-type-1` |
| Ganho de antena | 2 dBi |
| Largura de banda | 21,6 kHz |
| Temperatura de ruído | 150 K |
| Seletividade de canal adjacente (ACS) | 30 dB |
| Elevação mínima de operação | 10° |

### 3.3 ES Tipo 2 (7.1.5)

| Parâmetro | Valor |
|---|---|
| ID | `mss.2100MHz.7.1.5-ES-type-2` |
| Ganho de antena | 10 dBi |
| Largura de banda | 21,6 kHz |
| Temperatura de ruído | 150 K |
| Seletividade de canal adjacente (ACS) | 20 dB |
| Elevação mínima de operação | 10° |

---

## 4. Geometria e Posicionamento da Earth Station

| Parâmetro | Valor |
|---|---|
| Altura da ES | 1,5 m |
| Localização | Rede aleatória (posição dentro da área de serviço) |
| Distância mínima à BS (satélite) | 24 km (raio do feixe) |
| Azimute | Uniforme [−180°, +180°] |
| Elevação de apontamento | Uniforme [5°, 90°] |

A posição da ES é sorteada dentro da área de cobertura do feixe MSS DC a cada snapshot, mantendo distância mínima ao centro do feixe igual ao raio do feixe (24 km).

---

## 5. Modelo de Canal

| Parâmetro | Valor |
|---|---|
| Modelo de canal | **P.619** |
| Perda de polarização | 3 dB |
| Altura média de clutter | Baixa (`low`) — ambiente rural/pouco obstaculizado |
| Perda por clutter abaixo do telhado | 0 dB (não aplicada) |
| Latitude da ES (P.619) | −25,2637° |
| Altitude da ES (P.619) | 200 m |

---

## 6. Parâmetros Gerais da Simulação

| Parâmetro | Valor |
|---|---|
| Número de snapshots | 5000 |
| Semente aleatória | 82 |
| Sistema | `SINGLE_EARTH_STATION` |
| Enlace IMT | Downlink |
| Co-canal | Desabilitado |
| Canal adjacente | Habilitado |
| Cálculo de SINR intra-IMT DL | Desabilitado (otimização) |

---

## 7. Combinações de Simulação

O gerador de entradas (`generate_inputs.py`) cria arquivos para todas as combinações de:

- **1 sistema MSS DC** × **3 tipos de ES** × **2 fatores de carga** × **2 adjacências**

Totalizando **12 configurações** por execução.

| Dimensão | Valores |
|---|---|
| Sistema MSS DC | `imt.2110-2200MHz.mss-dc.system4-690km` |
| Earth Stations vítimas | System R (Forward), ES Tipo-1, ES Tipo-2 |
| Fator de carga MSS DC | 20%, 50% |
| Adjacências | 1ª (−5 MHz, ACLR 45 dB), 2ª (−10 MHz, ACLR 50 dB) |
