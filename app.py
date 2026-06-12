# Exemplo de como juntar a aquisição com a limpeza:
from src.extraction.aquisicao import load_crime_data, load_auxiliary_table
from src.pipeline.cleaning import execute_cleaning_pipeline

df_crime_bruto = load_crime_data()
df_aux_bruto = load_auxiliary_table()

df_crime_limpo, df_aux_limpo = execute_cleaning_pipeline(df_crime_bruto, df_aux_bruto)

df_crime_limpo, df_aux_limpo = execute_cleaning_pipeline(df_crime_bruto, df_aux_bruto)

print(f"Quantidade final de linhas (Crimes): {df_crime_limpo.shape[0]}")
print(f"Quantidade final de linhas (População): {df_aux_limpo.shape[0]}")