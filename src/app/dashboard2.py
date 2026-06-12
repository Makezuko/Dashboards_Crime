from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_layout(datasets):
    df_sunburst = datasets["sunburst_grupo_natureza"]
    df_heatmap = datasets["heatmap_grupo_dia"]
    df_barras = datasets["barras_faixa_grupo"]

    # 1. Sunburst / Treemap
    if df_sunburst.empty:
        fig_sunburst = go.Figure()
        fig_sunburst.update_layout(title="Sem dados para a Hierarquia")
    else:
        fig_sunburst = px.treemap(
            df_sunburst, 
            path=["NOME_MUNICIPIO", "GRUPO_CRIME"], 
            values="quantidade",
            title="Tipos de Crime por Cidade (Top 10)",
            color="GRUPO_CRIME"
        )
        fig_sunburst.update_layout(title_x=0.5)

    # 2. Heatmap
    if df_heatmap.empty:
        fig_heatmap = go.Figure()
        fig_heatmap.update_layout(title="Sem dados para Heatmap")
    else:
        ordem_dias = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
        heat_pivot = df_heatmap.pivot_table(
            index="GRUPO_CRIME", columns="DIA_SEMANA",
            values="quantidade", fill_value=0, observed=True
        )
        dias_cols = [d for d in ordem_dias if d in heat_pivot.columns]
        heat_pivot = heat_pivot[dias_cols]
        
        fig_heatmap = go.Figure(
            go.Heatmap(
                z=heat_pivot.values, 
                x=dias_cols, 
                y=heat_pivot.index.tolist(),
                colorscale="Reds",
                hovertemplate="<b>%{y}</b> — %{x}<br>%{z:,} ocorrencias<extra></extra>"
            )
        )
        fig_heatmap.update_layout(
            title="Intensidade: Grupo de Crime por Dia da Semana",
            title_x=0.5
        )

    # 3. Barras Empilhadas
    if df_barras.empty:
        fig_barras = go.Figure()
        fig_barras.update_layout(title="Sem dados para Faixa Horária")
    else:
        fig_barras = px.bar(
            df_barras, 
            x="FAIXA_HORARIA", 
            y="quantidade", 
            color="GRUPO_CRIME",
            barmode="stack",
            title="Distribuição por Faixa Horária e Grupo",
            labels={"quantidade": "Ocorrências", "FAIXA_HORARIA": "Período", "GRUPO_CRIME": "Grupo"}
        )
        fig_barras.update_layout(title_x=0.5)

    layout = html.Div([

        html.H1(
            "Dashboard de Criminalidade - Exploração",
            className="titulo"
        ),

        html.Div([

            html.Div(
                dcc.Graph(figure=fig_sunburst),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(figure=fig_heatmap),
                className="grafico-metade"
            )

        ], className="linha-graficos"),

        html.Div([

            html.Div(
                dcc.Graph(figure=fig_barras),
                style={"flex": "1", "padding": "10px", "width": "100%"}
            )

        ], className="linha-graficos")

    ])

    return layout
