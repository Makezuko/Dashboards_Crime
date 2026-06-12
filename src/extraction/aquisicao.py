import os
import pandas as pd

DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

def summarize_dataframe(df, name="DataFrame"):
    print("-" * 50)
    print(f"RESUMO DO DATAFRAME: {name}")
    print("-" * 50)
    
    print("\n[Formato / Dimensões]")
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")
    
    print("\n[Informações das Colunas e Tipos de Dados]")
    print(df.info())
    
    print("\n[Contagem de Valores Ausentes por Coluna]")
    missing_vals = df.isnull().sum()
    print(missing_vals[missing_vals > 0] if missing_vals.sum() > 0 else "Nenhum valor ausente encontrado.")
    
    print("\n[Métricas Estatísticas (Variáveis Numéricas)]")
    print(df.describe())
    
    print("\n[Métricas Estatísticas (Variáveis Categóricas)]")
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    if not categorical_cols.empty:
        print(df.describe(include=["object", "category"]))
    else:
        print("Nenhuma variável categórica encontrada.")
    print("-" * 50)

def load_crime_data():
    file_path = os.path.join(DATA_RAW_DIR, "SPDadosCriminais_2025.xlsx")
    df = pd.read_excel(file_path, engine="calamine")
    
    summarize_dataframe(df, name="SPDadosCriminais_2025")
    
    return df

def load_auxiliary_table():
    file_path = os.path.join(DATA_RAW_DIR, "Tabela 6579.csv")
    df = pd.read_csv(file_path)
    
    summarize_dataframe(df, name="Tabela 6579")
    
    return df

if __name__ == "__main__":
    print("Iniciando o diagnóstico de dados...\n")
    df_crime = load_crime_data()
    df_aux = load_auxiliary_table()