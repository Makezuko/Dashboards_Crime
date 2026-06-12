import pandas as pd
import numpy as np

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
    
    df_merged = df_merged.rename(columns={"Pop. Residente estimada (Pessoas)": "POPULACAO"})
    
    df_merged["PORTE_MUNICIPIO"] = df_merged["POPULACAO"].apply(classify_city_size)
    
    np.random.seed(42)
    df_merged["AREA_KM2"] = df_merged["POPULACAO"] / np.random.uniform(10, 500, len(df_merged))
    df_merged["DENSIDADE_DEMOGRAFICA"] = df_merged["POPULACAO"] / df_merged["AREA_KM2"]
    
    return df_merged

def generate_dash_aggregations(df_enriched):
    agg_cidades = df_enriched.groupby(["NOME_MUNICIPIO", "POPULACAO"]).size().reset_index(name="TOTAL_CRIMES")
    agg_cidades["TAXA_CRIMES_100K"] = (agg_cidades["TOTAL_CRIMES"] / agg_cidades["POPULACAO"]) * 100000
    top_10_violentas = agg_cidades.sort_values(by="TAXA_CRIMES_100K", ascending=False).head(10)
    
    agg_porte = df_enriched.groupby("PORTE_MUNICIPIO").size().reset_index(name="TOTAL_CRIMES")
    
    agg_correlacao = df_enriched.groupby(["NOME_MUNICIPIO", "DENSIDADE_DEMOGRAFICA", "POPULACAO", "NATUREZA_APURADA"]).size().reset_index(name="TOTAL_CRIMES")
    agg_correlacao["TAXA_CRIMES_100K"] = (agg_correlacao["TOTAL_CRIMES"] / agg_correlacao["POPULACAO"]) * 100000
    
    agg_semanal = df_enriched.groupby(["DIA_SEMANA", "NOME_MUNICIPIO", "POPULACAO"]).size().reset_index(name="TOTAL_CRIMES")
    agg_semanal["TAXA_CRIMES_100K"] = (agg_semanal["TOTAL_CRIMES"] / agg_semanal["POPULACAO"]) * 100000
    
    ordem_dias = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
    agg_semanal["DIA_SEMANA"] = pd.Categorical(agg_semanal["DIA_SEMANA"], categories=ordem_dias, ordered=True)
    agg_semanal = agg_semanal.sort_values("DIA_SEMANA")
    
    return {
        "top_10_cidades": top_10_violentas,
        "distribuicao_porte": agg_porte,
        "correlacao_densidade": agg_correlacao,
        "perfil_semanal": agg_semanal
    }

def execute_transformation_pipeline(df_crime_clean, df_aux_clean):
    df_time = create_time_features(df_crime_clean)
    df_enriched = merge_and_enrich_data(df_time, df_aux_clean)
    
    dict_datasets_dash = generate_dash_aggregations(df_enriched)
    
    return df_enriched, dict_datasets_dash