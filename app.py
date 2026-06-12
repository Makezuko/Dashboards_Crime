import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask
import dash

from src.extraction.aquisicao import (
    load_crime_data,
    load_auxiliary_table
)

from src.pipeline.cleaning import execute_cleaning_pipeline

from src.pipeline.transformation import (
    execute_transformation_pipeline,
    analyze_and_print_insights
)

from src.app.dashboard1 import init_dashboard


print("Carregando e processando os dados...")

df_crime_bruto = load_crime_data()
df_aux_bruto = load_auxiliary_table()

df_crime_limpo, df_aux_limpo = execute_cleaning_pipeline(
    df_crime_bruto,
    df_aux_bruto
)

df_enriched, dict_datasets_dash = execute_transformation_pipeline(
    df_crime_limpo,
    df_aux_limpo
)

analyze_and_print_insights(dict_datasets_dash)

assets_path = os.path.join(BASE_DIR, "assets")

server = Flask(__name__)

app_dash = dash.Dash(
    __name__,
    server=server,
    assets_folder=assets_path
)

init_dashboard(app_dash, dict_datasets_dash)

if __name__ == "__main__":
    server.run(debug=True, port=8050)