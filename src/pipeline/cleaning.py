import re
import pandas as pd

def clean_crime_data(df_raw):
    df = df_raw.copy()
    
    essential_cols = ["NUM_BO", "DATA_REGISTRO", "NOME_MUNICIPIO"]
    df = df.dropna(subset=essential_cols)
    
    df["DATA_OCORRENCIA_BO"] = pd.to_datetime(df["DATA_OCORRENCIA_BO"], errors="coerce")
    inicio_janela = "2025-07-01"
    fim_janela = "2025-12-31"
    df = df[(df["DATA_OCORRENCIA_BO"] >= inicio_janela) & (df["DATA_OCORRENCIA_BO"] <= fim_janela)]
    
    string_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip().str.upper()
        
    if "NOME_MUNICIPIO" in df.columns:
        df["NOME_MUNICIPIO"] = df["NOME_MUNICIPIO"].str.replace(r"[.-]", " ", regex=True)
        df["NOME_MUNICIPIO"] = df["NOME_MUNICIPIO"].str.replace(r"^S\s", "SÃO ", regex=True) # S.PAULO vira SÃO PAULO
    
    df["BAIRRO"] = df["BAIRRO"].fillna("NÃO INFORMADO")
    df["DESCR_CONDUTA"] = df["DESCR_CONDUTA"].fillna("NÃO ESPECIFICADA")
    
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        df = df[(df["LATITUDE"].notnull()) & (df["LONGITUDE"].notnull())]
        df = df[(df["LATITUDE"] != 0) & (df["LONGITUDE"] != 0)]
        
    df = df.drop_duplicates()
    
    return df

def clean_auxiliary_table(df_raw):
    df = df_raw.copy()
    
    df["Municipio"] = df["Municipio"].astype(str).str.strip().str.upper()
    df = df[df["Municipio"].str.endswith("(SP)")]
    df["Municipio"] = df["Municipio"].str.replace(r"\s*\(SP\)$", "", regex=True)
    
    df["Municipio"] = df["Municipio"].str.replace(r"[.-]", " ", regex=True)
    df["Municipio"] = df["Municipio"].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    
    return df

def clean_auxiliary_table(df_raw):
    df = df_raw.copy()
    
    df["Municipio"] = df["Municipio"].astype(str).str.strip().str.upper()
    
    df = df[df["Municipio"].str.endswith("(SP)")]
    
    df["Municipio"] = df["Municipio"].str.replace(r"\s*\(SP\)$", "", regex=True)
    
    return df

def validate_cleaned_data(df_crime, df_aux):
    print("=" * 50)
    print("INICIANDO VALIDAÇÃO DOS DADOS LIMPOS")
    print("=" * 50)
    
    ano_min = df_crime["DATA_OCORRENCIA_BO"].dt.year.min()
    ano_max = df_crime["DATA_OCORRENCIA_BO"].dt.year.max()
    mes_min = df_crime["DATA_OCORRENCIA_BO"].dt.month.min()
    
    if ano_min == 2025 and ano_max == 2025 and mes_min >= 7:
        print("Sucesso: Todos os dados pertencem a Julho-Dezembro de 2025.")
    else:
        print(f"Erro: Há datas fora do escopo! Encontrado de {ano_min} a {ano_max}.")

    null_counts = df_crime[["NUM_BO", "DATA_REGISTRO", "NOME_MUNICIPIO"]].isnull().sum().sum()
    if null_counts == 0:
        print("Sucesso: Nenhum valor nulo nas colunas críticas.")
    else:
        print(f"Erro: Foram encontrados {null_counts} valores nulos.")

    lat_zeros = (df_crime["LATITUDE"] == 0).sum()
    lon_zeros = (df_crime["LONGITUDE"] == 0).sum()
    if lat_zeros == 0 and lon_zeros == 0:
        print("Sucesso: Nenhuma coordenada zerada (0.0) encontrada.")
    else:
        print(f"Erro: Existem coordenadas zeradas na base.")

    cidades_com_sp = df_aux["Municipio"].str.contains(r"\(SP\)").sum()
    if cidades_com_sp == 0:
        print("Sucesso: O sufixo '(SP)' foi totalmente removido da tabela auxiliar.")
    else:
        print(f"Erro: Ainda existem municípios com '(SP)' no nome.")
        
    print("=" * 50 + "\n")

def execute_cleaning_pipeline(df_crime_raw, df_aux_raw):
    df_crime_clean = clean_crime_data(df_crime_raw)
    df_aux_clean = clean_auxiliary_table(df_aux_raw)
    
    validate_cleaned_data(df_crime_clean, df_aux_clean)
    
    return df_crime_clean, df_aux_clean