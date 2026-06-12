"""
data_pipeline.py — Pipeline Completo de Ciência de Dados
===========================================================
Etapas: Aquisição -> Integração -> Limpeza -> Transformação

Dados:
  1. SPDadosCriminais_2025.xlsx  — Ocorrências criminais SP (SSP-SP)
  2. populacao_municipios_SP_2025.csv — População estimada IBGE Tabela 6579
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  Caminhos dos arquivos
# ─────────────────────────────────────────────
PATH_CRIMES = "dados/SPDadosCriminais_2025.xlsx"
PATH_POPULACAO = "dados/populacao_municipios_SP_2025.csv"
PATH_CACHE = "dados/crimes_processado.pkl"


# ─────────────────────────────────────────────
#  ETAPA 1 — AQUISIÇÃO DE DADOS
# ─────────────────────────────────────────────
def carregar_crimes() -> pd.DataFrame:
    """
    Lê o arquivo Excel de ocorrências criminais da SSP-SP.
    Fonte: Portal de Transparência da SSP-SP
    """
    print("  [1/5] Carregando dados criminais (SSP-SP)...")
    df = pd.read_excel(PATH_CRIMES, sheet_name="JUL-DEZ_2025", engine="openpyxl")
    print(f"        -> {len(df):,} registros carregados | {df.shape[1]} colunas")
    return df


def carregar_populacao() -> pd.DataFrame:
    """
    Lê o arquivo CSV de população estimada por município (IBGE Tabela 6579).
    Coletado automaticamente via coleta_dados.py.
    """
    print("  [2/5] Carregando dados populacionais (IBGE Tabela 6579)...")
    df = pd.read_csv(PATH_POPULACAO, encoding="utf-8-sig", dtype={"COD_IBGE": str})
    print(f"        -> {len(df):,} municípios carregados")
    return df


# ─────────────────────────────────────────────
#  ETAPA 2 — INTEGRAÇÃO (MERGE)
# ─────────────────────────────────────────────
def integrar_dados(df_crimes: pd.DataFrame, df_pop: pd.DataFrame) -> pd.DataFrame:
    """
    Integra os dados criminais com os dados populacionais do IBGE
    via COD IBGE (chave comum entre os dois arquivos).
    """
    print("  [3/5] Integrando datasets (merge por COD IBGE)...")

    # O Excel armazena COD IBGE como float (ex: 3550308.0)
    # Precisamos converter para int -> string antes de fazer o merge
    # com o CSV do IBGE que usa string inteira (ex: "3550308")
    def normalizar_cod_ibge(series):
        return (
            pd.to_numeric(series, errors="coerce")  # float: 3550308.0
            .astype("Int64")                         # int:   3550308
            .astype(str)                             # str:   "3550308"
            .str.replace("<NA>", "")
            .str.strip()
        )

    df_crimes["COD IBGE NORM"] = normalizar_cod_ibge(df_crimes["COD IBGE"])
    df_pop["COD_IBGE_NORM"]    = df_pop["COD_IBGE"].astype(str).str.strip()

    df_merged = df_crimes.merge(
        df_pop[["COD_IBGE_NORM", "MUNICIPIO_NOME", "POPULACAO_ESTIMADA"]],
        left_on="COD IBGE NORM",
        right_on="COD_IBGE_NORM",
        how="left",
    )

    matched = df_merged["POPULACAO_ESTIMADA"].notna().sum()
    print(f"        -> {matched:,} registros com dados populacionais vinculados")
    print(f"        -> {len(df_merged) - matched:,} sem match (outros estados/etc.)")
    return df_merged



# ─────────────────────────────────────────────
#  ETAPA 3 — LIMPEZA E TRATAMENTO
# ─────────────────────────────────────────────
def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tratamento de:
    - Valores nulos
    - Encoding / caracteres especiais
    - Inconsistências
    - Padronização de formatos
    """
    print("  [4/5] Limpando e tratando dados...")

    # Remover linhas completamente nulas (7 linhas corrompidas identificadas)
    df = df.dropna(subset=["NOME_MUNICIPIO", "RUBRICA", "NATUREZA_APURADA"])
    print(f"        -> Após remoção de nulos críticos: {len(df):,} registros")

    # ── Datas ──────────────────────────────────────────────────────────
    df["DATA_OCORRENCIA_BO"] = pd.to_datetime(
        df["DATA_OCORRENCIA_BO"], errors="coerce"
    )
    df["DATA_REGISTRO"] = pd.to_datetime(df["DATA_REGISTRO"], errors="coerce")

    # ── Hora ───────────────────────────────────────────────────────────
    # HORA_OCORRENCIA_BO tem ~159k nulos -> "Não Informado"
    df["HORA_OCORRENCIA_BO"] = df["HORA_OCORRENCIA_BO"].astype(str)
    df["HORA_OCORRENCIA_BO"] = df["HORA_OCORRENCIA_BO"].replace(
        ["nan", "NaT", "None", ""], "Não Informado"
    )

    # ── Strings ────────────────────────────────────────────────────────
    str_cols = [
        "NOME_MUNICIPIO", "BAIRRO", "RUBRICA", "NATUREZA_APURADA",
        "DESCR_TIPOLOCAL", "DESCR_SUBTIPOLOCAL", "NOME_DEPARTAMENTO",
        "NOME_SECCIONAL", "DESC_PERIODO"
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.strip()
                .str.upper()
                .replace("NAN", np.nan)
            )

    # Padronizar DESC_PERIODO — ~414k nulos -> "NÃO INFORMADO"
    df["DESC_PERIODO"] = df["DESC_PERIODO"].fillna("NÃO INFORMADO")

    # ── Tipo local ─────────────────────────────────────────────────────
    df["DESCR_TIPOLOCAL"] = df["DESCR_TIPOLOCAL"].fillna("NÃO INFORMADO")
    df["DESCR_SUBTIPOLOCAL"] = df["DESCR_SUBTIPOLOCAL"].fillna("NÃO INFORMADO")

    # ── Mês/Ano ────────────────────────────────────────────────────────
    df["MES_ESTATISTICA"] = df["MES_ESTATISTICA"].fillna(0).astype(int)
    df["ANO_ESTATISTICA"] = df["ANO_ESTATISTICA"].fillna(2025).astype(int)

    print(f"        -> Limpeza concluída: {len(df):,} registros válidos")
    return df


# ─────────────────────────────────────────────
#  ETAPA 4 — TRANSFORMAÇÃO
# ─────────────────────────────────────────────
def transformar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Criação de novas variáveis e agregações:
    - Nome do mês
    - Faixa horária (Madrugada/Manhã/Tarde/Noite)
    - Grupo de crime simplificado
    - Taxa de crimes por 100k habitantes
    - Dia da semana
    """
    print("  [5/5] Transformando e criando novas variáveis...")

    # ── Nome do mês ────────────────────────────────────────────────────
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    df["MES_NOME"] = df["MES_ESTATISTICA"].map(meses).fillna("Desconhecido")

    # ── Faixa horária ──────────────────────────────────────────────────
    def extrair_hora(s):
        try:
            partes = str(s).split(":")
            return int(partes[0])
        except Exception:
            return -1

    df["HORA_NUM"] = df["HORA_OCORRENCIA_BO"].apply(extrair_hora)

    def faixa_horaria(h):
        if h < 0:
            return "Não Informado"
        elif 0 <= h < 6:
            return "Madrugada (00h–05h)"
        elif 6 <= h < 12:
            return "Manhã (06h–11h)"
        elif 12 <= h < 18:
            return "Tarde (12h–17h)"
        else:
            return "Noite (18h–23h)"

    df["FAIXA_HORARIA"] = df["HORA_NUM"].apply(faixa_horaria)

    # ── Dia da semana ──────────────────────────────────────────────────
    dias = {
        0: "Segunda", 1: "Terça", 2: "Quarta",
        3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"
    }
    df["DIA_SEMANA"] = df["DATA_OCORRENCIA_BO"].dt.dayofweek.map(dias)
    df["DIA_SEMANA"] = df["DIA_SEMANA"].fillna("Não Informado")

    # ── Grupo de crime simplificado (vetorizado) ───────────────────────
    # Nota: NATUREZA_APURADA e RUBRICA já estão em UPPERCASE após a etapa de limpeza
    nat = df["NATUREZA_APURADA"].astype(str)
    rub = df["RUBRICA"].astype(str).str.upper()

    # Strings reais encontradas nos dados (verificado na exploração):
    # "LESÃO CORPORAL CULPOSA POR ACIDENTE DE TRÂNSITO"
    # "HOMICÍDIO CULPOSO POR ACIDENTE DE TRÂNSITO"
    # "FURTO DE VEÍCULO", "ROUBO DE VEÍCULO"
    # Ordem importa: Trânsito antes de Furto/Roubo/Lesão (subcategoria)
    condicoes = [
        nat.str.contains("ACIDENTE DE TR", na=False) |
        nat.str.contains("CULPOSA POR ACIDENTE", na=False) |
        nat.str.contains("CULPOSO POR ACIDENTE", na=False) |
        rub.str.contains("303|302|AUTOMOTOR", na=False),
        nat.str.contains("FURTO", na=False) | rub.str.contains("FURTO", na=False),
        nat.str.contains("ROUBO", na=False) | rub.str.contains("ROUBO", na=False),
        nat.str.contains("LESÃO CORPORAL|LESAO CORPORAL", na=False) |
        rub.str.contains("LESÃO|LESAO", na=False),
        nat.str.contains("HOMICIDIO|HOMICÍDIO|FEMINICIDIO|FEMINICÍDIO", na=False) |
        rub.str.contains("HOMICIDIO|HOMICÍDIO|FEMINICIDIO|FEMINICÍDIO", na=False),
        nat.str.contains("ESTUPRO", na=False) | rub.str.contains("ESTUPRO", na=False),
        nat.str.contains("TRAFICO|TRÁFICO|ENTORPECENTE|APREENSAO DE ENTORPECENTE|"
                         "PORTE DE ENTORPECENTE", na=False) |
        rub.str.contains("TRAFICO|TRÁFICO|DROGA|ENTORPECENTE|ASSOCIA", na=False),
        nat.str.contains("PORTE DE ARMA|APREENSAO DE ARMA|PORTE ILEGAL", na=False) |
        rub.str.contains("ARMA|PORTE", na=False),
    ]
    escolhas = [
        "Trânsito",
        "Furto", "Roubo", "Lesão Corporal",
        "Homicídio", "Crimes Sexuais", "Drogas", "Armas",
    ]
    df["GRUPO_CRIME"] = np.select(condicoes, escolhas, default="Outros")


    # ── Taxa por 100k habitantes ───────────────────────────────────────
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(
        df["POPULACAO_ESTIMADA"], errors="coerce"
    )
    # Calculada por município — será usada nas agregações
    df["CRIMES_POR_100K"] = np.where(
        df["POPULACAO_ESTIMADA"] > 0,
        (1 / df["POPULACAO_ESTIMADA"]) * 100_000,
        np.nan
    )

    # ── Semana do mês (para análise de calendário) ─────────────────────
    df["SEMANA_MES"] = df["DATA_OCORRENCIA_BO"].dt.isocalendar().week.astype("Int64")

    print(f"        -> Novas colunas: MES_NOME, FAIXA_HORARIA, DIA_SEMANA, GRUPO_CRIME, CRIMES_POR_100K")
    print(f"        -> Grupos de crime: {df['GRUPO_CRIME'].value_counts().to_dict()}")
    return df


# ─────────────────────────────────────────────
#  FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────
def executar_pipeline(forcar_reprocessamento: bool = False) -> pd.DataFrame:
    """
    Executa o pipeline completo ou carrega do cache se disponível.
    """
    if not forcar_reprocessamento and os.path.exists(PATH_CACHE):
        print("  Carregando dados do cache (processamento anterior)...")
        df = pd.read_pickle(PATH_CACHE)
        print(f"  Cache carregado: {len(df):,} registros")
        return df

    print("\n" + "=" * 60)
    print("  PIPELINE DE CIÊNCIA DE DADOS — CRIMES SP 2025")
    print("=" * 60 + "\n")

    # Etapas 1-2: Aquisição
    df_crimes = carregar_crimes()
    df_pop = carregar_populacao()

    # Etapa 2: Integração
    df = integrar_dados(df_crimes, df_pop)

    # Etapa 3: Limpeza
    df = limpar_dados(df)

    # Etapa 4: Transformação
    df = transformar_dados(df)

    # Salvar cache para performance
    os.makedirs("dados", exist_ok=True)
    df.to_pickle(PATH_CACHE)
    print(f"\n  Cache salvo em: {PATH_CACHE}")
    print(f"\n  Pipeline concluído! Dataset final: {len(df):,} registros | {df.shape[1]} colunas")
    print("=" * 60 + "\n")

    return df


# ─────────────────────────────────────────────
#  AGREGAÇÕES PARA OS DASHBOARDS
# ─────────────────────────────────────────────
def get_crimes_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Agregação mensal para gráfico de tendência."""
    ordem_meses = ["Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    agg = (
        df.groupby(["MES_NOME", "GRUPO_CRIME"], observed=True)
        .size()
        .reset_index(name="TOTAL")
    )
    agg["MES_ORD"] = pd.Categorical(agg["MES_NOME"], categories=ordem_meses, ordered=True)
    return agg.sort_values("MES_ORD")


def get_top_municipios(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Top N municípios por total de ocorrências e taxa per capita."""
    agg = (
        df.groupby("NOME_MUNICIPIO", observed=True)
        .agg(
            TOTAL=("RUBRICA", "count"),
            POPULACAO=("POPULACAO_ESTIMADA", "first"),
        )
        .reset_index()
    )
    agg["TAXA_100K"] = np.where(
        agg["POPULACAO"] > 0,
        (agg["TOTAL"] / agg["POPULACAO"]) * 100_000,
        np.nan
    )
    return agg.nlargest(n, "TOTAL")


def get_crimes_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    """Distribuição por grupo de crime."""
    return (
        df.groupby("GRUPO_CRIME", observed=True)
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL", ascending=False)
    )


def get_heatmap_hora_dia(df: pd.DataFrame) -> pd.DataFrame:
    """Matriz: Faixa horária × Dia da semana para heatmap."""
    dias_ordem = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    horas_ordem = [
        "Madrugada (00h–05h)", "Manhã (06h–11h)",
        "Tarde (12h–17h)", "Noite (18h–23h)"
    ]
    agg = (
        df[df["FAIXA_HORARIA"] != "Não Informado"]
        .groupby(["DIA_SEMANA", "FAIXA_HORARIA"], observed=True)
        .size()
        .reset_index(name="TOTAL")
    )
    agg["DIA_ORD"] = pd.Categorical(agg["DIA_SEMANA"], categories=dias_ordem, ordered=True)
    agg["HORA_ORD"] = pd.Categorical(agg["FAIXA_HORARIA"], categories=horas_ordem, ordered=True)
    return agg.sort_values(["DIA_ORD", "HORA_ORD"])


def get_crimes_por_local(df: pd.DataFrame) -> pd.DataFrame:
    """Distribuição por tipo de local."""
    return (
        df.groupby("DESCR_TIPOLOCAL", observed=True)
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL", ascending=False)
        .head(12)
    )


def get_crimes_municipio_grupo(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top municípios com breakdown por grupo de crime (barras empilhadas)."""
    top_muns = df["NOME_MUNICIPIO"].value_counts().head(top_n).index.tolist()
    agg = (
        df[df["NOME_MUNICIPIO"].isin(top_muns)]
        .groupby(["NOME_MUNICIPIO", "GRUPO_CRIME"], observed=True)
        .size()
        .reset_index(name="TOTAL")
    )
    return agg


if __name__ == "__main__":
    df = executar_pipeline(forcar_reprocessamento=True)
    print("\nInfo do dataset processado:")
    print(f"  Registros: {len(df):,}")
    print(f"  Colunas: {list(df.columns)}")
    print(f"\nGrupos de crime:")
    print(df["GRUPO_CRIME"].value_counts().to_string())
    print(f"\nFaixas horárias:")
    print(df["FAIXA_HORARIA"].value_counts().to_string())
