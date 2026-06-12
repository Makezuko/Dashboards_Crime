from dash import html, dcc, Input, Output
import plotly.express as px
from src.app.components.filters import create_filters
import pandas as pd

def init_dashboard(app, datasets):

    top10 = datasets["top_10_cidades"]
    porte = datasets["distribuicao_porte"]
    perfil = datasets["perfil_semanal"]
    correlacao = datasets["correlacao_populacao"]
    natureza_porte = datasets["natureza_porte"]
    natureza_semana = datasets["natureza_semana"]

    fig_ranking_porte = px.bar(
        porte.sort_values("TOTAL_CRIMES"),
        x="TOTAL_CRIMES",
        y="PORTE_MUNICIPIO",
        orientation="h",
        title="Ranking dos Portes de Município"
    )

    fig_ranking_porte.update_layout(
        title_x=0.5,
        yaxis={"categoryorder": "total ascending"}
    )

    perfil_total = (
        perfil
        .groupby(
            "DIA_SEMANA",
            observed=True
        )["TOTAL_CRIMES"]
        .sum()
        .reset_index()
    )

    top_crimes = (
        natureza_porte
        .groupby(
            "NATUREZA_APURADA"
        )["TOTAL"]
        .sum()
        .reset_index()
        .sort_values(
            by="TOTAL",
            ascending=False
        )
        .head(10)
    )

    fig_top_crimes = px.bar(
        top_crimes.sort_values("TOTAL"),
        x="TOTAL",
        y="NATUREZA_APURADA",
        orientation="h",
        title="10 Tipos de Crime Mais Frequentes",
        labels={
            "TOTAL": "Quantidade",
            "NATUREZA_APURADA": "Natureza"
        }
    )

    fig_top_crimes.update_layout(
        title_x=0.5,
        yaxis={"categoryorder": "total ascending"}
    )

    participacao = top_crimes.copy()

    participacao["PERCENTUAL"] = (
        participacao["TOTAL"]
        / participacao["TOTAL"].sum()
        * 100
    )

    fig_participacao = px.pie(
        participacao,
        names="NATUREZA_APURADA",
        values="PERCENTUAL",
        title="Participação de Cada Tipo de Crime"
    )

    fig_participacao.update_layout(
        title_x=0.5
    )

    # --- MODELO CORRIGIDO: SEM LEGENDA SOBREPOSTA E COM MARGENS CORRETAS (INICIAL) ---
    fig_natureza_porte = px.bar(
        natureza_porte,
        x="TOTAL",
        y="PORTE_MUNICIPIO",
        color="NATUREZA_APURADA",
        orientation="h",
        title="Distribuição Relativa de Crimes por Porte do Município",
        labels={
            "PORTE_MUNICIPIO": "Porte do Município",
            "TOTAL": "Proporção",
            "NATUREZA_APURADA": "Natureza"
        }
    )

    fig_natureza_porte.update_layout(
        title_x=0.5,
        title_font=dict(size=16, family="Arial, sans-serif"),
        barmode="stack",      
        barnorm="percent",    
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,     # Remove a legenda poluída que invadiu o gráfico
        margin=dict(l=180, r=30, t=50, b=50), # Dá espaço na esquerda para os textos longos dos Portes
        xaxis=dict(ticksuffix="%") # Adiciona símbolo de porcentagem no eixo X
    )
    # Ajusta as caixas interativas do mouse para mostrar o valor formatado de forma limpa
    fig_natureza_porte.update_traces(hovertemplate="<b>%{hovertext}</b><br>Proporção: %{x:.2f}%<extra></extra>")
    # ----------------------------------------------------------------------------------

    heatmap_data = (
        natureza_semana
        .pivot_table(
            index="NATUREZA_APURADA",
            columns="DIA_SEMANA",
            values="TOTAL",
            aggfunc="sum"
        )
        .fillna(0)
    )

    fig_heatmap = px.imshow(
        heatmap_data,
        aspect="auto",
        title="Tipos de Crime por Dia da Semana",
        labels={
            "x": "Dia da Semana",
            "y": "Natureza do Crime",
            "color": "Ocorrências"
        },
        color_continuous_scale="Reds"  
    )
    
    fig_heatmap.update_layout(
        title_x=0.5,
        title_font=dict(size=16, family="Arial, sans-serif"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=150, r=20, t=50, b=50),  
        coloraxis_colorbar=dict(
            title="Qtd",
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=150,
            yanchor="middle", y=0.5
        )
    )
    fig_heatmap.update_yaxes(tickfont=dict(size=11))  

    diversidade_crimes = (
        natureza_porte
        .groupby("PORTE_MUNICIPIO")["NATUREZA_APURADA"]
        .nunique()
        .reset_index()
    )

    fig_diversidade = px.bar(
        diversidade_crimes,
        x="PORTE_MUNICIPIO",
        y="NATUREZA_APURADA",
        title="Quantidade de Tipos de Crime por Porte",
        labels={
            "NATUREZA_APURADA": "Número de tipos de crime",
            "PORTE_MUNICIPIO": "Porte"
        }
    )

    fig_diversidade.update_layout(
        title_x=0.5
    )

    app.layout = html.Div([

        html.H1(
            "Dashboard de Criminalidade - Exploração Interativa",
            className="titulo"
        ),
        create_filters(
            natureza_porte,
            natureza_semana
        ),
        html.Div([

            html.Div(
                dcc.Graph(
                    id="grafico-top-crimes",
                    figure=fig_top_crimes
                ),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(
                    id="grafico-natureza-porte",
                    figure=fig_natureza_porte
                ),
                className="grafico-metade"
            ),

        ], className="linha-graficos"),

        html.Div([

            html.Div(
                dcc.Graph(
                    id="grafico-heatmap",
                    figure=fig_heatmap
                ),
                className="grafico-metade"
            )

        ], className="linha-graficos"),

        html.Div([
            html.Div(
                dcc.Graph(
                    figure=fig_participacao
                ),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(
                    figure=fig_ranking_porte
                ),
                className="grafico-metade"
            )

        ], className="linha-graficos"),

    ])

    @app.callback(
        Output("grafico-top-crimes", "figure"),
        Output("grafico-natureza-porte", "figure"),
        Output("grafico-heatmap", "figure"),
        Input("filtro-porte", "value"),
        Input("filtro-dia", "value")
    )
    def atualizar_graficos(porte_selecionado, dia_selecionado):

        df_porte = natureza_porte.copy()
        df_semana = naturezas_semana.copy() if 'naturezas_semana' in locals() else natureza_semana.copy()

        if porte_selecionado:
            df_porte = df_porte[
                df_porte["PORTE_MUNICIPIO"] == porte_selecionado
            ]

            naturezas_validas = (
                df_porte["NATUREZA_APURADA"]
                .unique()
            )

            df_semana = df_semana[
                df_semana["NATUREZA_APURADA"]
                .isin(naturezas_validas)
            ]

        if porte_selecionado:
            naturezas_validas = (
                df_porte["NATUREZA_APURADA"]
                .unique()
            )

            df_semana = df_semana[
                df_semana["NATUREZA_APURADA"]
                .isin(naturezas_validas)
            ]

        if dia_selecionado:
            df_semana = df_semana[
                df_semana["DIA_SEMANA"] == dia_selecionado
            ]

        top_crimes = (
            df_porte
            .groupby("NATUREZA_APURADA")["TOTAL"]
            .sum()
            .reset_index()
            .sort_values(by="TOTAL", ascending=False)
            .head(10)
        )

        fig_top_crimes = px.bar(
            top_crimes.sort_values("TOTAL"),
            x="TOTAL",
            y="NATUREZA_APURADA",
            orientation="h",
            title="10 Tipos de Crime Mais Frequentes"
        )

        # --- MODELO CORRIGIDO REPLICADO DENTRO DO CALLBACK ---
        fig_natureza_porte = px.bar(
            df_porte,
            x="TOTAL",
            y="PORTE_MUNICIPIO",
            color="NATUREZA_APURADA",
            orientation="h",
            title="Distribuição Relativa de Crimes por Porte do Município",
            labels={
                "PORTE_MUNICIPIO": "Porte do Município",
                "TOTAL": "Proporção",
                "NATUREZA_APURADA": "Natureza"
            }
        )

        fig_natureza_porte.update_layout(
            title_x=0.5,
            title_font=dict(size=16, family="Arial, sans-serif"),
            barmode="stack",      
            barnorm="percent",    
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,     # Mantém limpo após filtragem externa
            margin=dict(l=180, r=30, t=50, b=50),
            xaxis=dict(ticksuffix="%")
        )
        fig_natureza_porte.update_traces(hovertemplate="<b>%{hovertext}</b><br>Proporção: %{x:.2f}%<extra></extra>")
        # -------------------------------------------------------------------

        ordem_dias = [
            "SEGUNDA",
            "TERÇA",
            "QUARTA",
            "QUINTA",
            "SEXTA",
            "SÁBADO",
            "DOMINGO"
        ]

        df_semana["DIA_SEMANA"] = pd.Categorical(
            df_semana["DIA_SEMANA"],
            categories=ordem_dias,
            ordered=True
        )

        heatmap_data = (
            df_semana
            .pivot_table(
                index="NATUREZA_APURADA",
                columns="DIA_SEMANA",
                values="TOTAL",
                aggfunc="sum"
            )
            .fillna(0)
        )

        fig_heatmap = px.imshow(
            heatmap_data,
            aspect="auto",
            title="Natureza dos Crimes por Dia da Semana",
            labels={
                "x": "Dia da Semana",
                "y": "Natureza do Crime",
                "color": "Ocorrências"
            },
            color_continuous_scale="Reds"  
        )

        fig_heatmap.update_layout(
            title_x=0.5,
            title_font=dict(size=16, family="Arial, sans-serif"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=150, r=20, t=50, b=50),
            coloraxis_colorbar=dict(
                title="Qtd",
                thicknessmode="pixels", thickness=15,
                lenmode="pixels", len=150,
                yanchor="middle", y=0.5
            )
        )
        fig_heatmap.update_yaxes(tickfont=dict(size=11))

        return (
            fig_top_crimes,
            fig_natureza_porte,
            fig_heatmap
        )

    return app