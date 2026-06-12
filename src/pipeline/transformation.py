import pandas as pd
import numpy as np

ORDEM_HORARIO = ["Madrugada (00h–05h)", "Manhã (06h–11h)", "Tarde (12h–17h)", "Noite (18h–23h)"]
GRUPOS_VALIDOS = ["Furto", "Roubo", "Lesão Corporal", "Trânsito", "Drogas",
                  "Crimes Sexuais", "Homicídio", "Armas"]

def map_grupo_crime(natureza):
    nat = str(natureza).upper()
    if "FURTO" in nat: return "Furto"
    elif "ROUBO" in nat or "LATROCÍNIO" in nat or "EXTORSÃO" in nat: return "Roubo"
    elif "LESÃO CORPORAL" in nat: return "Lesão Corporal"
    elif "TRÂNSITO" in nat or "EMBRIAGUEZ" in nat or "HOMICÍDIO CULPOSO POR VEÍCULO" in nat: return "Trânsito"
    elif "ENTORPECENTES" in nat or "DROGAS" in nat: return "Drogas"
    elif "ESTUPRO" in nat or "SEXUAL" in nat or "ASSEDIAR" in nat: return "Crimes Sexuais"
    elif "HOMICÍDIO" in nat or "FEMINICÍDIO" in nat: return "Homicídio"
    elif "ARMA" in nat or "MUNIÇÃO" in nat: return "Armas"
    else: return "Outros"

def map_faixa_horaria(hora_str):
    if pd.isna(hora_str): return "Não Informado"
    hora_str = str(hora_str).strip()
    if hora_str == "Não Informado" or hora_str == "": return "Não Informado"
    try:
        h = int(hora_str.split(":")[0])
        if 0 <= h <= 5: return "Madrugada (00h–05h)"
        elif 6 <= h <= 11: return "Manhã (06h–11h)"
        elif 12 <= h <= 17: return "Tarde (12h–17h)"
        else: return "Noite (18h–23h)"
    except:
        return "Não Informado"

def create_time_features(df):
    df_time = df.copy()
    
    if "DATA_OCORRENCIA_BO" in df_time.columns:
        df_time["MES_NOME"] = df_time["DATA_OCORRENCIA_BO"].dt.strftime("%B")
        
        dias_pt = {
            0: "SEGUNDA", 1: "TERÇA", 2: "QUARTA", 
            3: "QUINTA", 4: "SEXTA", 5: "SÁBADO", 6: "DOMINGO"
        }
        df_time["DIA_SEMANA"] = df_time["DATA_OCORRENCIA_BO"].dt.dayofweek.map(dias_pt)
        df_time["EH_FIM_SEMANA"] = df_time["DATA_OCORRENCIA_BO"].dt.dayofweek.isin([5, 6]).astype(int)

    if "NATUREZA_APURADA" in df_time.columns:
        df_time["GRUPO_CRIME"] = df_time["NATUREZA_APURADA"].apply(map_grupo_crime)
        
    if "HORA_OCORRENCIA_BO" in df_time.columns:
        df_time["FAIXA_HORARIA"] = df_time["HORA_OCORRENCIA_BO"].apply(map_faixa_horaria)
        
    return df_time

def classify_city_size(populacao):
    if populacao < 50000:
        return "PEQUENO PORTE (<50K HAB)"
    elif 50000 <= populacao <= 300000:
        return "MÉDIO PORTE (50K-300K HAB)"
    else:
        return "GRANDE PORTE (>300K HAB)"

def merge_and_enrich_data(df_crime, df_aux):
    df_merged = pd.merge(
        df_crime,
        df_aux,
        left_on="NOME_MUNICIPIO",
        right_on="Municipio",
        how="inner"
    )

    df_merged = df_merged.rename(
        columns={"Pop. Residente estimada (Pessoas)": "POPULACAO"}
    )

    df_merged["PORTE_MUNICIPIO"] = (
        df_merged["POPULACAO"]
        .apply(classify_city_size)
    )

    return df_merged

def get_sunburst_data(df):
    grupos_validos = [g for g in GRUPOS_VALIDOS if g in df["GRUPO_CRIME"].unique()]
    result = (
        df[df["GRUPO_CRIME"].isin(grupos_validos)]
        .groupby(["NOME_MUNICIPIO", "GRUPO_CRIME"], observed=True)
        .size()
        .reset_index(name="quantidade")
    )
    # Filter top 10 cities by total volume to keep the treemap readable
    top_cidades = result.groupby("NOME_MUNICIPIO", observed=True)["quantidade"].sum().nlargest(10).index
    result = result[result["NOME_MUNICIPIO"].isin(top_cidades)]
    return result

def get_heatmap_group_weekday(df):
    ordem_dias = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
    dias_validos = [d for d in ordem_dias if d in df["DIA_SEMANA"].unique()]
    grupos_validos = [g for g in GRUPOS_VALIDOS if g in df["GRUPO_CRIME"].unique()]

    result = (
        df[df["DIA_SEMANA"].isin(dias_validos) & df["GRUPO_CRIME"].isin(grupos_validos)]
        .groupby(["GRUPO_CRIME", "DIA_SEMANA"], observed=True)
        .size()
        .reset_index(name="quantidade")
    )
    result["DIA_SEMANA"] = pd.Categorical(result["DIA_SEMANA"], categories=ordem_dias, ordered=True)
    result["GRUPO_CRIME"] = pd.Categorical(result["GRUPO_CRIME"], categories=grupos_validos, ordered=True)
    return result.sort_values(["GRUPO_CRIME", "DIA_SEMANA"])

def get_crimes_by_hour_group(df):
    horarios_validos = [h for h in ORDEM_HORARIO if h in df["FAIXA_HORARIA"].unique()]
    grupos_validos = [g for g in GRUPOS_VALIDOS if g in df["GRUPO_CRIME"].unique()]

    result = (
        df[df["FAIXA_HORARIA"].isin(horarios_validos) & df["GRUPO_CRIME"].isin(grupos_validos)]
        .groupby(["FAIXA_HORARIA", "GRUPO_CRIME"], observed=True)
        .size()
        .reset_index(name="quantidade")
    )
    result["FAIXA_HORARIA"] = pd.Categorical(
        result["FAIXA_HORARIA"], categories=ORDEM_HORARIO, ordered=True
    )
    return result.sort_values("FAIXA_HORARIA")

def generate_dash_aggregations(df_enriched):
    agg_cidades = df_enriched.groupby(["NOME_MUNICIPIO", "POPULACAO"]).size().reset_index(name="TOTAL_CRIMES")
    agg_cidades["TAXA_CRIMES_100K"] = (agg_cidades["TOTAL_CRIMES"] / agg_cidades["POPULACAO"]) * 100000
    top_10_violentas = agg_cidades.sort_values(by="TAXA_CRIMES_100K", ascending=False).head(10)
    
    agg_porte = df_enriched.groupby("PORTE_MUNICIPIO").size().reset_index(name="TOTAL_CRIMES")
    
    agg_correlacao = (df_enriched.groupby(["NOME_MUNICIPIO", "POPULACAO"]).size().reset_index(name="TOTAL_CRIMES"))
    agg_correlacao["TAXA_CRIMES_100K"] = (agg_correlacao["TOTAL_CRIMES"]/ agg_correlacao["POPULACAO"]) * 100000
    
    agg_semanal = df_enriched.groupby(["DIA_SEMANA", "NOME_MUNICIPIO", "POPULACAO"]).size().reset_index(name="TOTAL_CRIMES")
    agg_semanal["TAXA_CRIMES_100K"] = (agg_semanal["TOTAL_CRIMES"] / agg_semanal["POPULACAO"]) * 100000
    
    ordem_dias = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
    agg_semanal["DIA_SEMANA"] = pd.Categorical(agg_semanal["DIA_SEMANA"], categories=ordem_dias, ordered=True)
    agg_semanal = agg_semanal.sort_values("DIA_SEMANA")
    
    # 1. Cruzamento de Natureza por Porte de Município
    agg_natureza_porte = df_enriched.groupby(["PORTE_MUNICIPIO", "NATUREZA_APURADA"]).size().reset_index(name="TOTAL")

    # 2. Cruzamento de Natureza por Dia da Semana (Efeito Fim de Semana)
    agg_natureza_semana = df_enriched.groupby(["DIA_SEMANA", "NATUREZA_APURADA"], observed=True).size().reset_index(name="TOTAL")

    return {
        "top_10_cidades": top_10_violentas,
        "distribuicao_porte": agg_porte,
        "correlacao_populacao": agg_correlacao,
        "perfil_semanal": agg_semanal,
        "natureza_porte": agg_natureza_porte,
        "natureza_semana": agg_natureza_semana,
        "sunburst_grupo_natureza": get_sunburst_data(df_enriched),
        "heatmap_grupo_dia": get_heatmap_group_weekday(df_enriched),
        "barras_faixa_grupo": get_crimes_by_hour_group(df_enriched)
    }

def execute_transformation_pipeline(df_crime_clean, df_aux_clean):
    df_time = create_time_features(df_crime_clean)
    df_enriched = merge_and_enrich_data(df_time, df_aux_clean)
    
    dict_datasets_dash = generate_dash_aggregations(df_enriched)
    
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
    print(f"\n💡 CONCLUSÃO: A cidade proporcionalmente mais violenta é {cidade_topo}, com uma taxa de {taxa_topo:.2f} crimes por 100 mil habitantes, superando a média das demais.")

    # distribuição por porte dos municípios
    print("\n" + "-" * 40)
    print(" DISTRIBUIÇÃO POR PORTE DOS MUNICÍPIOS")
    df_porte = dict_datasets_dash["distribuicao_porte"].copy()
    total_crimes = df_porte["TOTAL_CRIMES"].sum()
    df_porte["PERCENTUAL"] = (df_porte["TOTAL_CRIMES"] / total_crimes) * 100
    
    for row in df_porte.itertuples():
        print(f"- {row.PORTE_MUNICIPIO}: {row.TOTAL_CRIMES} crimes ({row.PERCENTUAL:.2f}%)")
        
    porte_mais_violento = df_porte.loc[df_porte["TOTAL_CRIMES"].idxmax()]
    print(f"\n💡 CONCLUSÃO: O fenômeno da interiorização se confirma? A maior concentração absoluta de crimes está em municípios de {porte_mais_violento['PORTE_MUNICIPIO']} com {porte_mais_violento['PERCENTUAL']:.2f}% dos casos.")

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
        f"\n💡 CONCLUSÃO: A relação entre tamanho da população "
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
    print(f"\n💡 CONCLUSÃO: O pico da atividade criminal ocorre na {dia_pico['DIA_SEMANA']}, concentrando {dia_pico['PERCENTUAL']:.2f}% das ocorrências do semestre. Alocação preventiva recomendada para este dia.")
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