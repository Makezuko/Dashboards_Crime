import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, ctx

import src.app.dashboard1 as d1
import src.app.dashboard2 as d2
from src.app.components.filters import navbar, tab_bar

from src.extraction.aquisicao import load_crime_data, load_auxiliary_table
from src.pipeline.cleaning import execute_cleaning_pipeline
from src.pipeline.transformation import execute_transformation_pipeline

root_path = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(root_path, "assets")

print("Carregando e processando os dados do zero...")
df_crime_bruto = load_crime_data()
df_aux_bruto = load_auxiliary_table()

df_crime_limpo, df_aux_limpo = execute_cleaning_pipeline(df_crime_bruto, df_aux_bruto)
df_enriched, dict_datasets_dash = execute_transformation_pipeline(df_crime_limpo, df_aux_limpo)

print(f"Dados finais preparados: {len(df_enriched):,} registros prontos para o Dash")

app = Dash(
    __name__,
    assets_folder=assets_path,
    suppress_callback_exceptions=True,
    title="Criminalidade SP 2025",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Dashboard de criminalidade no Estado de Sao Paulo — Jul a Dez 2025"},
    ],
)

app.layout = html.Div(
    [
        dcc.Store(id="current-theme",      data="dark"),
        dcc.Store(id="current-tab",        data="d1"),
        dcc.Store(id="theme-applied-store", data="dark"),

        navbar(),
        tab_bar("d1"),

        html.Div(id="tab-content"),
    ],
    id="root",
)

@app.callback(
    Output("current-theme",   "data"),
    Output("theme-btn-dark",  "className"),
    Output("theme-btn-mid",   "className"),
    Output("theme-btn-light", "className"),
    Input("theme-btn-dark",   "n_clicks"),
    Input("theme-btn-mid",    "n_clicks"),
    Input("theme-btn-light",  "n_clicks"),
    Input("current-theme",    "data"),
)
def switch_theme(n_dark, n_mid, n_light, current):
    triggered = ctx.triggered_id
    theme_map = {
        "theme-btn-dark":  "dark",
        "theme-btn-mid":   "mid",
        "theme-btn-light": "light",
    }
    new_theme = theme_map.get(triggered, current or "dark")

    classes = {
        "dark":  ("theme-btn active", "theme-btn",        "theme-btn"),
        "mid":   ("theme-btn",        "theme-btn active",  "theme-btn"),
        "light": ("theme-btn",        "theme-btn",        "theme-btn active"),
    }
    return (new_theme, *classes[new_theme])

app.clientside_callback(
    """
    function(theme) {
        document.documentElement.setAttribute('data-theme', theme || 'dark');
        return theme;
    }
    """,
    Output("theme-applied-store", "data"),
    Input("current-theme", "data"),
)

@app.callback(
    Output("tab-content",  "children"),
    Output("tab-d1",       "className"),
    Output("tab-d2",       "className"),
    Output("current-tab",  "data"),
    Input("tab-d1",        "n_clicks"),
    Input("tab-d2",        "n_clicks"),
    Input("current-tab",   "data"),
)
def switch_tab(n_d1, n_d2, current_tab):
    triggered = ctx.triggered_id

    if triggered == "tab-d2":
        active = "d2"
    elif triggered == "tab-d1":
        active = "d1"
    else:
        active = current_tab or "d1"

    cls_d1 = "tab-link active" if active == "d1" else "tab-link"
    cls_d2 = "tab-link active" if active == "d2" else "tab-link"
    
    content = d1.layout(df_enriched) if active == "d1" else d2.layout(df_enriched)
    return content, cls_d1, cls_d2, active

d1.register_callbacks(app, dict_datasets_dash)
d2.register_callbacks(app, dict_datasets_dash)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)