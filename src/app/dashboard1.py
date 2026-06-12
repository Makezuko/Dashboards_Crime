from dash import html, dcc
import plotly.express as px


def init_dashboard(app, datasets):

    top10 = datasets["top_10_cidades"]
    porte = datasets["distribuicao_porte"]
    perfil = datasets["perfil_semanal"]
    correlacao = datasets["correlacao_populacao"]

    total_crimes = porte["TOTAL_CRIMES"].sum()

    cidade_mais_violenta = top10.iloc[0]["NOME_MUNICIPIO"]

    taxa_maxima = round(
        top10.iloc[0]["TAXA_CRIMES_100K"],
        2
    )

    qtd_cidades = perfil["NOME_MUNICIPIO"].nunique()

    perfil_total = (
        perfil
        .groupby(
            "DIA_SEMANA",
            observed=True
        )["TOTAL_CRIMES"]
        .sum()
        .reset_index()
    )

    fig_semana = px.line(
        perfil_total,
        x="DIA_SEMANA",
        y="TOTAL_CRIMES",
        markers=True,
        title="Ocorrências por Dia da Semana"
    )

    fig_semana.update_layout(
        title_x=0.5
    )

    fig_correlacao = px.scatter(
        correlacao,
        x="POPULACAO",
        y="TAXA_CRIMES_100K",
        title="População × Taxa de Crimes",
        opacity=0.6,
        labels={
            "POPULACAO": "População",
            "TAXA_CRIMES_100K": "Taxa por 100 mil habitantes"
        },
        hover_data=["NOME_MUNICIPIO"]
    )

    fig_correlacao.update_layout(
        title_x=0.5
    )

    fig_porte = px.pie(
        porte,
        names="PORTE_MUNICIPIO",
        values="TOTAL_CRIMES",
        title="Distribuição dos Crimes por Porte do Município"
    )

    fig_porte.update_layout(
        title_x=0.5
    )

    fig_top10 = px.bar(
        top10.sort_values("TAXA_CRIMES_100K"),
        x="TAXA_CRIMES_100K",
        y="NOME_MUNICIPIO",
        orientation="h",
        title="Top 10 Cidades Mais Violentas por Taxa",
        labels={
            "TAXA_CRIMES_100K": "Taxa por 100 mil habitantes",
            "NOME_MUNICIPIO": "Município"
        }
    )

    fig_top10.update_layout(
        title_x=0.5,
        yaxis={"categoryorder": "total ascending"}
    )

    fig_populacao = px.bar(
        top10.sort_values("POPULACAO"),
        x="POPULACAO",
        y="NOME_MUNICIPIO",
        orientation="h",
        title="População das 10 Cidades Mais Violentas",
        labels={
            "POPULACAO": "População",
            "NOME_MUNICIPIO": "Município"
        }
    )

    fig_populacao.update_layout(
        title_x=0.5,
        yaxis={"categoryorder": "total ascending"}
    )

    app.layout = html.Div([

        html.H1(
            "Dashboard de Criminalidade - Visão Geral",
            className="titulo"
        ),

        html.Div([

            html.Div([
                html.H3("Total de Crimes"),
                html.H2(f"{total_crimes:,}")
            ], className="card"),

            html.Div([
                html.H3("Cidade Mais Violenta"),
                html.H2(cidade_mais_violenta)
            ], className="card"),

            html.Div([
                html.H3("Maior Taxa por 100 mil hab."),
                html.H2(f"{taxa_maxima:.2f}")
            ], className="card"),

            html.Div([
                html.H3("Municípios Analisados"),
                html.H2(qtd_cidades)
            ], className="card")

        ], className="cards-container"),

        html.Div([

            html.Div(
                dcc.Graph(
                    figure=fig_semana
                ),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(
                    figure=fig_correlacao
                ),
                className="grafico-metade"
            )

        ], className="linha-graficos"),

        html.Div([

            html.Div(
                dcc.Graph(
                    figure=fig_porte
                ),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(
                    figure=fig_top10
                ),
                className="grafico-metade"
            )

        ], className="linha-graficos"),

        html.Div([

            html.Div(
                dcc.Graph(
                    figure=fig_populacao
                ),
                className="grafico-metade"
            )

        ], className="linha-graficos")

    ])

    return app

