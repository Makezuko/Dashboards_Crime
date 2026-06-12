# 🛡️ Dashboard Criminal SP 2025

Dashboard interativo de análise dos dados criminais do Estado de São Paulo (Jul–Dez 2025), desenvolvido com **Python + Dash + Plotly**.

## 📊 Visão Geral

| Item | Detalhe |
|------|---------|
| **Registros** | 573.335 ocorrências criminais |
| **Período** | Julho a Dezembro de 2025 |
| **Fonte 1** | [SSP-SP — Portal de Transparência](https://www.ssp.sp.gov.br/transparenciassp/) |
| **Fonte 2** | [IBGE SIDRA Tabela 6579](https://sidra.ibge.gov.br/Tabela/6579) — Estimativas populacionais |
| **Municípios** | 645 municípios do Estado de SP |

## 🏗️ Estrutura do Projeto

```
Dashboards_Crime/
├── app.py                    # Aplicação Dash principal (multi-page)
├── data_pipeline.py          # Pipeline completo: leitura → limpeza → transformação
├── coleta_dados.py           # Script de coleta automática (IBGE via API SIDRA) 🎯 BÔNUS
├── requirements.txt          # Dependências Python
├── dados/
│   ├── SPDadosCriminais_2025.xlsx          # Dados SSP-SP (arquivo principal)
│   └── populacao_municipios_SP_2025.csv    # Dados IBGE (coletados automaticamente)
├── pages/
│   ├── dashboard1.py         # Dashboard 1: Visão Geral Executiva
│   └── dashboard2.py         # Dashboard 2: Exploração Interativa
└── assets/
    └── style.css             # Tema dark premium
```

## 🚀 Como Executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. (Opcional) Reexecutar coleta de dados do IBGE
python coleta_dados.py

# 3. Iniciar o dashboard
python app.py
```

Acesse em: **http://127.0.0.1:8050**

## 📈 Pipeline de Dados

```
SPDadosCriminais_2025.xlsx          populacao_municipios_SP_2025.csv
         │                                         │
         ▼                                         ▼
   pd.read_excel()                          pd.read_csv()
         │                                         │
         └──────────── pd.merge() ────────────────┘
                            │ (chave: COD IBGE)
                            ▼
                     Limpeza e Tratamento
                    (encoding, nulos, datas)
                            │
                            ▼
                      Transformação
              (GRUPO_CRIME, FAIXA_HORARIA, TAXA_100K...)
                            │
                            ▼
                    Dashboard Interativo
```

## 🖥️ Dashboards

### Dashboard 1 — Visão Geral Executiva
- 5 KPI cards (total, crime top, cidade top, mês, homicídios)
- Evolução mensal de ocorrências
- Distribuição por grupo de crime (donut)
- Top 10 tipos de crime (horizontal bar)
- Top 10 municípios
- Crimes por tipo de local

### Dashboard 2 — Exploração Interativa
- **4 filtros**: Município, Grupo de Crime, Período (meses), Faixa Horária
- **6 visualizações**:
  1. Série temporal por grupo de crime
  2. Heatmap: Dia da semana × Faixa horária
  3. Barras empilhadas: Municípios × Grupo de crime
  4. Treemap: Hierarquia Município → Tipo de Crime
  5. Crimes por tipo de local
  6. Dispersão: Taxa per capita × População

## 💡 Principais Insights

1. **Furto domina** — 55% das ocorrências; presente em todos os municípios
2. **Concentração em SP capital** — 40% das ocorrências em uma cidade
3. **Pico no horário noturno** — Roubos e homicídios concentrados à noite
4. **Via pública como epicentro** — Maioria dos crimes em espaços abertos
5. **Violência no trânsito expressiva** — 37k+ lesões culposas por acidente
6. **Disparidade per capita** — Municípios pequenos têm taxas elevadas

## 🎯 Script de Coleta Automática (Bônus +1pt)

O arquivo `coleta_dados.py` coleta automaticamente os dados populacionais do IBGE via API pública (SIDRA), demonstrando:
- Requisição HTTP à API REST do IBGE
- Parsing de resposta JSON
- Transformação e exportação para CSV

```bash
python coleta_dados.py
```

## 📦 Dependências

```
dash, dash-bootstrap-components, plotly, pandas, openpyxl, requests
```