"""
coleta_dados.py — Script de Coleta Automática de Dados (BÔNUS +1pt)
=======================================================================
Este script coleta automaticamente os dados populacionais do IBGE via
API pública SIDRA (Tabela 6579 — Estimativas de População por Município).

Fonte: https://sidra.ibge.gov.br/Tabela/6579
API:   https://api.sidra.ibge.gov.br/
"""

import requests
import pandas as pd
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def coletar_populacao_sp(ano: int = 2025, salvar: bool = True) -> pd.DataFrame:
    """
    Coleta os dados de população estimada de todos os municípios do
    Estado de São Paulo (código IBGE: 35) via API SIDRA.

    Parâmetros:
    -----------
    ano     : Ano de referência (padrão: 2025)
    salvar  : Se True, salva o CSV na pasta 'dados/'

    Retorna:
    --------
    DataFrame com colunas: COD_IBGE, MUNICIPIO_IBGE, MUNICIPIO_NOME,
                            POPULACAO_ESTIMADA, ANO
    """
    print("=" * 60)
    print(f"  Coletando dados IBGE — Tabela 6579 | Ano: {ano}")
    print("  Fonte: api.sidra.ibge.gov.br (dados públicos)")
    print("=" * 60)

    # API SIDRA IBGE — Tabela 6579, Variável 9324 (pop. estimada)
    # n6/in n3 35 → municípios do estado de SP (código 35)
    url = (
        f"http://api.sidra.ibge.gov.br/values/"
        f"t/6579/n6/in%20n3%2035/v/9324/p/{ano}?formato=json"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DashboardCrime/1.0; Academic)"
    }

    try:
        print(f"\n  Requisição HTTP para: {url}")
        response = requests.get(url, headers=headers, timeout=60, verify=False)
        response.raise_for_status()
        print(f"  Status: {response.status_code} OK")
    except requests.RequestException as e:
        print(f"  ERRO ao acessar a API: {e}")
        raise

    data = response.json()
    if not data or len(data) < 2:
        raise ValueError("API retornou dados inválidos ou vazios.")

    # Primeira linha é o cabeçalho
    header_row = data[0]
    rows = data[1:]

    # Construir DataFrame
    df = pd.DataFrame(rows, columns=list(header_row.keys()))

    # Renomear colunas para nomes legíveis
    rename_map = {
        "V": "POPULACAO_ESTIMADA",
        "D1C": "COD_IBGE",
        "D1N": "MUNICIPIO_IBGE",
        "D3N": "ANO",
    }
    df = df.rename(columns=rename_map)

    # Conversões de tipo
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")
    df["COD_IBGE"] = df["COD_IBGE"].astype(str).str.strip()

    # Extrair nome limpo (sem " - SP")
    df["MUNICIPIO_NOME"] = (
        df["MUNICIPIO_IBGE"].str.replace(r"\s*-\s*SP$", "", regex=True).str.strip()
    )

    # Selecionar colunas finais
    cols = ["COD_IBGE", "MUNICIPIO_IBGE", "MUNICIPIO_NOME", "POPULACAO_ESTIMADA", "ANO"]
    cols_exist = [c for c in cols if c in df.columns]
    df_final = df[cols_exist].copy()

    # Estatísticas
    total_mun = len(df_final)
    total_pop = df_final["POPULACAO_ESTIMADA"].sum()
    print(f"\n  Municípios coletados : {total_mun}")
    print(f"  População total SP   : {total_pop:,.0f} habitantes")

    # Salvar CSV
    if salvar:
        os.makedirs("dados", exist_ok=True)
        out_path = f"dados/populacao_municipios_SP_{ano}.csv"
        df_final.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"  Arquivo salvo em     : {out_path}")

    print("\n  Coleta concluída com sucesso!")
    print("=" * 60)
    return df_final


if __name__ == "__main__":
    df = coletar_populacao_sp(ano=2025, salvar=True)
    print("\nAmostra dos dados coletados:")
    print(df.head(10).to_string(index=False))
