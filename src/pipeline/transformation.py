import pandas as pd
import numpy as np


def create_time_features(df):
    df_time = df.copy()

    if "DATA_OCORRENCIA_BO" in df_time.columns:
        df_time["MES_NOME"] = df_time["DATA_OCORRENCIA_BO"].dt.strftime("%B")

        dias_pt = {
            0: "SEGUNDA",
            1: "TERÇA",
            2: "QUARTA",
            3: "QUINTA",
            4: "SEXTA",
            5: "SÁBADO",
            6: "DOMINGO"
        }

        df_time["DIA_SEMANA"] = (
            df_time["DATA_OCORRENCIA_BO"]
            .dt.dayofweek
            .map(dias_pt)
        )

        df_time["EH_FIM_SEMANA"] = (
            df_time["DATA_OCORRENCIA_BO"]
            .dt.dayofweek
            .isin([5, 6])
            .astype(int)
        )

    return df_time


def classify_city_size(populacao):
    if populacao < 50000:
        return "PEQUENO PORTE (<50K HAB)"
    elif 50000 <= populacao <= 300000:
        return "MÉDIO PORTE (50K-300K HAB)"
    else:
        return "GRANDE PORTE (>300K HAB)"


def classify_crime_group(natureza):
    natureza_upper = str(natureza).upper()
    if "FURTO" in natureza_upper:
        return "Furto"
    if "ROUBO" in natureza_upper or "LATROCÍNIO" in natureza_upper or "LATROCINIO" in natureza_upper:
        return "Roubo"
    if "HOMICÍDIO" in natureza_upper or "HOMICIDIO" in natureza_upper:
        return "Homicídio"
    if "LESÃO" in natureza_upper or "LESAO" in natureza_upper:
        return "Lesão Corporal"
    if "ENTORPECENTE" in natureza_upper or "TRÁFICO" in natureza_upper or "TRAFICO" in natureza_upper:
        return "Drogas"
    if "ARMA" in natureza_upper:
        return "Armas"
    if "TRÂNSITO" in natureza_upper or "TRANSITO" in natureza_upper:
        return "Trânsito"
    return "Outros"


def classify_time_period(hora):
    try:
        h = int(str(hora).split(":")[0])
    except (ValueError, IndexError):
        return "Indefinido"
    if 0 <= h <= 5:
        return "Madrugada (00h–05h)"
    if 6 <= h <= 11:
        return "Manhã (06h–11h)"
    if 12 <= h <= 17:
        return "Tarde (12h–17h)"
    if 18 <= h <= 23:
        return "Noite (18h–23h)"
    return "Indefinido"


def merge_and_enrich_data(df_crime, df_aux):
    df_merged = pd.merge(
        df_crime,
        df_aux,
        left_on="NOME_MUNICIPIO",
        right_on="Municipio",
        how="inner"
    )

    df_merged = df_merged.rename(
        columns={
            "Pop. Residente estimada (Pessoas)": "POPULACAO"
        }
    )

    df_merged["PORTE_MUNICIPIO"] = (
        df_merged["POPULACAO"]
        .apply(classify_city_size)
    )

    df_merged["GRUPO"] = (
        df_merged["NATUREZA_APURADA"]
        .apply(classify_crime_group)
    )

    if "HORA_OCORRENCIA_BO" in df_merged.columns:
        df_merged["FAIXA_HORARIA"] = (
            df_merged["HORA_OCORRENCIA_BO"]
            .apply(classify_time_period)
        )

    return df_merged


def generate_dash_aggregations(df_enriched):

    agg_cidades = (
        df_enriched
        .groupby(
            ["NOME_MUNICIPIO", "POPULACAO"]
        )
        .size()
        .reset_index(name="TOTAL_CRIMES")
    )

    agg_cidades["TAXA_CRIMES_100K"] = (
        agg_cidades["TOTAL_CRIMES"]
        / agg_cidades["POPULACAO"]
    ) * 100000

    top_10_violentas = (
        agg_cidades
        .sort_values(
            by="TAXA_CRIMES_100K",
            ascending=False
        )
        .head(10)
    )

    agg_porte = (
        df_enriched
        .groupby("PORTE_MUNICIPIO")
        .size()
        .reset_index(name="TOTAL_CRIMES")
    )

    agg_correlacao = (
        df_enriched
        .groupby(
            ["NOME_MUNICIPIO", "POPULACAO"]
        )
        .size()
        .reset_index(name="TOTAL_CRIMES")
    )

    agg_correlacao["TAXA_CRIMES_100K"] = (
        agg_correlacao["TOTAL_CRIMES"]
        / agg_correlacao["POPULACAO"]
    ) * 100000

    agg_semanal = (
        df_enriched
        .groupby(
            ["DIA_SEMANA", "NOME_MUNICIPIO", "POPULACAO"]
        )
        .size()
        .reset_index(name="TOTAL_CRIMES")
    )

    agg_semanal["TAXA_CRIMES_100K"] = (
        agg_semanal["TOTAL_CRIMES"]
        / agg_semanal["POPULACAO"]
    ) * 100000

    ordem_dias = [
        "SEGUNDA",
        "TERÇA",
        "QUARTA",
        "QUINTA",
        "SEXTA",
        "SÁBADO",
        "DOMINGO"
    ]

    agg_semanal["DIA_SEMANA"] = pd.Categorical(
        agg_semanal["DIA_SEMANA"],
        categories=ordem_dias,
        ordered=True
    )

    agg_semanal = agg_semanal.sort_values("DIA_SEMANA")

    agg_natureza_porte = (
        df_enriched
        .groupby(
            ["PORTE_MUNICIPIO", "NATUREZA_APURADA"]
        )
        .size()
        .reset_index(name="TOTAL")
    )

    agg_natureza_semana = (
        df_enriched
        .groupby(
            ["DIA_SEMANA", "NATUREZA_APURADA"],
            observed=True
        )
        .size()
        .reset_index(name="TOTAL")
    )

    agg_sunburst = (
        df_enriched
        .groupby(
            ["NOME_MUNICIPIO", "NATUREZA_APURADA"]
        )
        .size()
        .reset_index(name="TOTAL")
    )

    agg_grupo_semana = (
        df_enriched
        .groupby(
            ["DIA_SEMANA", "GRUPO"],
            observed=True
        )
        .size()
        .reset_index(name="TOTAL")
    )

    agg_grupo_faixa = pd.DataFrame()
    if "FAIXA_HORARIA" in df_enriched.columns:
        agg_grupo_faixa = (
            df_enriched[
                df_enriched["FAIXA_HORARIA"] != "Indefinido"
            ]
            .groupby(
                ["FAIXA_HORARIA", "GRUPO"]
            )
            .size()
            .reset_index(name="TOTAL")
        )

    return {
        "top_10_cidades": top_10_violentas,
        "distribuicao_porte": agg_porte,
        "correlacao_populacao": agg_correlacao,
        "perfil_semanal": agg_semanal,
        "natureza_porte": agg_natureza_porte,
        "natureza_semana": agg_natureza_semana,
        "sunburst_cidade_natureza": agg_sunburst,
        "grupo_semana": agg_grupo_semana,
        "grupo_faixa_horaria": agg_grupo_faixa
    }


def execute_transformation_pipeline(
        df_crime_clean,
        df_aux_clean):

    df_time = create_time_features(df_crime_clean)

    df_enriched = merge_and_enrich_data(
        df_time,
        df_aux_clean
    )

    dict_datasets_dash = generate_dash_aggregations(
        df_enriched
    )

    return df_enriched, dict_datasets_dash

def analyze_and_print_insights(dict_datasets_dash):
    print("=" * 40)
    print(" ANALISE CRÍTICA E INSIGHTS DOS DADOS ")
    print("=" * 40)
    
    # top 10 Cidades
    print("\n TOP 10 CIDADES MAIS VIOLENTAS")
    df_top10 = dict_datasets_dash["top_10_cidades"]
    for i, row in enumerate(df_top10.itertuples(), 1):
        print(f"{i}º {row.NOME_MUNICIPIO} | Taxa: {row.TAXA_CRIMES_100K:.2f} por 100k hab. (Pop: {int(row.POPULACAO)})")
    
    cidade_topo = df_top10.iloc[0]["NOME_MUNICIPIO"]
    taxa_topo = df_top10.iloc[0]["TAXA_CRIMES_100K"]
    print(f"\nCONCLUSÃO: A cidade proporcionalmente mais violenta é {cidade_topo}, com uma taxa de {taxa_topo:.2f} crimes por 100 mil habitantes, superando a média das demais.")

    # distribuição por porte dos municípios
    print("\n" + "-" * 40)
    print(" DISTRIBUIÇÃO POR PORTE DOS MUNICÍPIOS")
    df_porte = dict_datasets_dash["distribuicao_porte"].copy()
    total_crimes = df_porte["TOTAL_CRIMES"].sum()
    df_porte["PERCENTUAL"] = (df_porte["TOTAL_CRIMES"] / total_crimes) * 100
    
    for row in df_porte.itertuples():
        print(f"- {row.PORTE_MUNICIPIO}: {row.TOTAL_CRIMES} crimes ({row.PERCENTUAL:.2f}%)")
        
    porte_mais_violento = df_porte.loc[df_porte["TOTAL_CRIMES"].idxmax()]
    print(f"\nCONCLUSÃO: O fenômeno da interiorização se confirma? A maior concentração absoluta de crimes está em municípios de {porte_mais_violento['PORTE_MUNICIPIO']} com {porte_mais_violento['PERCENTUAL']:.2f}% dos casos.")

    print("\n" + "-" * 40)
    print(" RELAÇÃO ENTRE POPULAÇÃO E TAXA DE CRIMINALIDADE")

    df_corr = dict_datasets_dash["correlacao_populacao"]

    correlacao_geral = (
        df_corr["POPULACAO"]
        .corr(df_corr["TAXA_CRIMES_100K"])
    )

    print(
        f"Coeficiente de correlação (População vs Taxa): "
        f"{correlacao_geral:.4f}"
    )

    status_corr = (
        "forte"
        if abs(correlacao_geral) > 0.7
        else "moderada"
        if abs(correlacao_geral) > 0.4
        else "fraca ou inexistente"
    )

    print(
        f"\nCONCLUSÃO: A relação entre tamanho da população "
        f"e taxa de criminalidade é {status_corr} "
        f"({correlacao_geral:.2f})."
    )

    print(
        "Isso mostra que municípios maiores não são "
        "necessariamente os mais violentos proporcionalmente."
    )
    # dia da semana com mais crimes 
    print("\n" + "-" * 40)
    print(" PERFIL SEMANAL DA VIOLÊNCIA")
    df_semana = dict_datasets_dash["perfil_semanal"]
    
    df_dias_agg = df_semana.groupby("DIA_SEMANA", observed=True)["TOTAL_CRIMES"].sum().reset_index()
    total_semana = df_dias_agg["TOTAL_CRIMES"].sum()
    df_dias_agg["PERCENTUAL"] = (df_dias_agg["TOTAL_CRIMES"] / total_semana) * 100
    
    for row in df_dias_agg.itertuples():
        print(f"- {row.DIA_SEMANA}: {row.TOTAL_CRIMES} crimes ({row.PERCENTUAL:.2f}%)")
        
    dia_pico = df_dias_agg.loc[df_dias_agg["TOTAL_CRIMES"].idxmax()]
    print(f"\nCONCLUSÃO: O pico da atividade criminal ocorre na {dia_pico['DIA_SEMANA']}, concentrando {dia_pico['PERCENTUAL']:.2f}% das ocorrências do semestre. Alocação preventiva recomendada para este dia.")
    print("=" * 40)

    agg_natureza_porte = dict_datasets_dash["natureza_porte"]
    agg_natureza_semana = dict_datasets_dash["natureza_semana"]
    
    #top 3 crimes por porte de cidade
    print("\n[INSIGHT] TOP 3 CRIMES MAIS COMUNS POR PORTE DE CIDADE:")

    df_ordenado_porte = agg_natureza_porte.sort_values(by=["PORTE_MUNICIPIO", "TOTAL"], ascending=[True, False])
    df_top3_porte = df_ordenado_porte.groupby("PORTE_MUNICIPIO").head(3)
    
    porte_atual = None
    for row in df_top3_porte.itertuples():
        if row.PORTE_MUNICIPIO != porte_atual:
            porte_atual = row.PORTE_MUNICIPIO
            print(f"\n• Cidades de {porte_atual}:")
        print(f"  - {row.NATUREZA_APURADA}: {row.TOTAL} casos")

    # crime mais comum por porte de cidade
    print("\n CRIME MAIS COMUM POR PORTE DE CIDADE:")
    idx_max_porte = agg_natureza_porte.groupby("PORTE_MUNICIPIO")["TOTAL"].idxmax()
    df_predominante_porte = agg_natureza_porte.loc[idx_max_porte]
    
    for row in df_predominante_porte.itertuples():
        print(f"- Cidades de {row.PORTE_MUNICIPIO}: A maior incidência é de '{row.NATUREZA_APURADA}' ({row.TOTAL} casos).")
        
    # crime no fds vs crime em dias uteis
    print("\n" + "-" * 50)
    print(" COMPORTAMENTO DAS NATUREZAS NO FIM DE SEMANA:")
    
    # Filtra os dois dias mais críticos do fim de semana para ver o top 3 crimes
    df_fds = agg_natureza_semana[agg_natureza_semana["DIA_SEMANA"].isin(["SÁBADO", "DOMINGO"])]
    df_fds_agg = df_fds.groupby("NATUREZA_APURADA")["TOTAL"].sum().reset_index()
    top_3_fds = df_fds_agg.sort_values(by="TOTAL", ascending=False).head(3)
    
    print("Top 3 crimes com maior volume combinados no Sábado e Domingo:")
    for row in top_3_fds.itertuples():
        print(f"- {row.NATUREZA_APURADA}: {row.TOTAL} ocorrências")