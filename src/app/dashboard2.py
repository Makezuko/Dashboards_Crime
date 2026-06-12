from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from src.app.components.filters import create_filters
import pandas as pd

# ---------------------------------------------------------------------------
# Paleta de cores padronizada por tipo de crime (NATUREZA_APURADA)
# Usada em todos os gráficos que colorem por natureza do crime.
# ---------------------------------------------------------------------------
CRIME_COLOR_MAP = {
    # Furtos
    "FURTO DE VEÍCULO":                     "#E63946",
    "FURTO - OUTROS":                        "#FF6B6B",
    "FURTO DE CARGA":                        "#FF8FA3",
    # Roubos
    "ROUBO - OUTROS":                        "#2D6A4F",
    "ROUBO DE VEÍCULO":                      "#40916C",
    "ROUBO DE CARGA":                        "#52B788",
    "ROUBO A BANCO":                         "#74C69D",
    # Lesão corporal
    "LESÃO CORPORAL DOLOSA":                 "#E76F51",
    "LESÃO CORPORAL CULPOSA - OUTRAS":       "#F4A261",
    "LESÃO CORPORAL CULPOSA POR ACIDENTE DE TRÂNSITO": "#FCBF49",
    # Homicídio
    "HOMICÍDIO DOLOSO":                      "#6D023A",
    "HOMICÍDIO CULPOSO POR ACIDENTE DE TRÂNSITO": "#9E0059",
    "TENTATIVA DE HOMICÍDIO":               "#C9184A",
    # Drogas
    "TRÁFICO DE ENTORPECENTES":              "#7B2D8B",
    "USO DE ENTORPECENTES":                  "#A663CC",
    # Armas
    "PORTE DE ARMA":                         "#343A8C",
    "DISPARO DE ARMA DE FOGO":              "#4361EE",
    # Trânsito
    "DIREÇÃO PERIGOSA":                      "#F77F00",
    "EMBRIAGUEZ AO VOLANTE":                 "#FCBF49",
    # Crimes sexuais
    "ESTUPRO":                               "#9C4221",
    "ESTUPRO DE VULNERÁVEL":                "#C05621",
    # Outros
    "OUTROS":                                "#8D99AE",
}

def init_dashboard(app, datasets, df_enriched=None):

    top10 = datasets["top_10_cidades"]
    porte = datasets["distribuicao_porte"]
    perfil = datasets["perfil_semanal"]
    correlacao = datasets["correlacao_populacao"]
    natureza_porte = datasets["natureza_porte"]
    natureza_semana = datasets["natureza_semana"]
    sunburst_data = datasets["sunburst_cidade_natureza"]
    grupo_semana = datasets["grupo_semana"]
    grupo_faixa = datasets["grupo_faixa_horaria"]

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
        color="NATUREZA_APURADA",
        orientation="h",
        title="10 Tipos de Crime Mais Frequentes",
        labels={
            "TOTAL": "Quantidade",
            "NATUREZA_APURADA": "Natureza"
        },
        color_discrete_map=CRIME_COLOR_MAP
    )

    fig_top_crimes.update_layout(
        title_x=0.5,
        yaxis={"categoryorder": "total ascending"},
        showlegend=False
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
        title="Participação de Cada Tipo de Crime",
        color="NATUREZA_APURADA",
        color_discrete_map=CRIME_COLOR_MAP
    )

    fig_participacao.update_layout(
        title_x=0.5
    )

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
        },
        color_discrete_map=CRIME_COLOR_MAP
    )

    fig_natureza_porte.update_layout(
        title_x=0.5,
        title_font=dict(size=16, family="Arial, sans-serif"),
        barmode="stack",
        barnorm="percent",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=180, r=30, t=50, b=50),
        xaxis=dict(ticksuffix="%")
    )
    fig_natureza_porte.update_traces(hovertemplate="<b>%{hovertext}</b><br>Proporção: %{x:.2f}%<extra></extra>")

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

    # Treemap: top 10 cidades com mais crimes, mostrando as categorias mais repetidas
    sunburst_top = (
        sunburst_data
        .sort_values("TOTAL", ascending=False)
    )
    top_cidades = (
        sunburst_top
        .groupby("NOME_MUNICIPIO")["TOTAL"]
        .sum()
        .nlargest(10)
        .index
    )
    sunburst_filtrado = sunburst_top[
        sunburst_top["NOME_MUNICIPIO"].isin(top_cidades)
    ]

    fig_sunburst = px.treemap(
        sunburst_filtrado,
        path=["NOME_MUNICIPIO", "NATUREZA_APURADA"],
        values="TOTAL",
        color="NATUREZA_APURADA",
        color_discrete_map=CRIME_COLOR_MAP,
        title="Categorias de Crime por Cidade (Top 10)"
    )

    fig_sunburst.update_layout(
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig_sunburst.update_traces(
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>Ocorrências: %{value:,}<br>% da cidade: %{percentParent:.1%}<extra></extra>"
    )

    ordem_dias = [
        "SEGUNDA",
        "TERÇA",
        "QUARTA",
        "QUINTA",
        "SEXTA",
        "SÁBADO",
        "DOMINGO"
    ]

    grupo_semana_pivot = (
        grupo_semana
        .pivot_table(
            index="GRUPO",
            columns="DIA_SEMANA",
            values="TOTAL",
            aggfunc="sum"
        )
        .fillna(0)
    )

    cols_ordenadas = [d for d in ordem_dias if d in grupo_semana_pivot.columns]
    grupo_semana_pivot = grupo_semana_pivot[cols_ordenadas]

    fig_grupo_heatmap = px.imshow(
        grupo_semana_pivot,
        aspect="auto",
        title="Intensidade: Grupo de Crime por Dia da Semana",
        labels={
            "x": "Dia da Semana",
            "y": "Grupo",
            "color": "Ocorrências"
        },
        color_continuous_scale="Reds"
    )

    fig_grupo_heatmap.update_layout(
        title_x=0.5,
        title_font=dict(size=16, family="Arial, sans-serif"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=150, r=20, t=50, b=50)
    )

    ordem_faixas = [
        "Madrugada (00h–05h)",
        "Manhã (06h–11h)",
        "Tarde (12h–17h)",
        "Noite (18h–23h)"
    ]

    fig_faixa_horaria = px.bar(
        grupo_faixa,
        x="FAIXA_HORARIA",
        y="TOTAL",
        color="GRUPO",
        title="Distribuição por Faixa Horária e Grupo",
        labels={
            "FAIXA_HORARIA": "Faixa Horária",
            "TOTAL": "Ocorrências",
            "GRUPO": "Grupo"
        },
        category_orders={"FAIXA_HORARIA": ordem_faixas}
    )

    fig_faixa_horaria.update_layout(
        title_x=0.5,
        barmode="stack"
    )

    app.layout = html.Div([

        html.H1(
            "Dashboard de Criminalidade - Exploração Interativa",
            className="titulo"
        ),
        create_filters(
            natureza_porte,
            natureza_semana,
            df_enriched
        ),
        html.Div([

            html.Div(
                dcc.Graph(
                    id="grafico-sunburst",
                    figure=fig_sunburst
                ),
                className="grafico-metade"
            ),

            html.Div(
                dcc.Graph(
                    id="grafico-grupo-heatmap",
                    figure=fig_grupo_heatmap
                ),
                className="grafico-metade"
            ),

        ], className="linha-graficos"),

        html.Div([

            html.Div(
                dcc.Graph(
                    id="grafico-faixa-horaria",
                    figure=fig_faixa_horaria
                ),
                className="grafico-full"
            )

        ], className="linha-graficos"),

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
        Output("grafico-sunburst", "figure"),
        Output("grafico-grupo-heatmap", "figure"),
        Output("grafico-faixa-horaria", "figure"),
        Input("filtro-porte", "value"),
        Input("filtro-dia", "value"),
        Input("filtro-cidade", "value")
    )
    def atualizar_graficos(porte_selecionado, dia_selecionado, cidade_selecionada):
        if df_enriched is not None:
            df_filtered = df_enriched.copy()
            
            if porte_selecionado:
                df_filtered = df_filtered[df_filtered["PORTE_MUNICIPIO"] == porte_selecionado]
                
            if cidade_selecionada:
                df_filtered = df_filtered[df_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
                
            if dia_selecionado:
                df_filtered = df_filtered[df_filtered["DIA_SEMANA"] == dia_selecionado]

            # 1. 10 Tipos de Crime Mais Frequentes
            top_crimes_upd = (
                df_filtered
                .groupby("NATUREZA_APURADA")
                .size()
                .reset_index(name="TOTAL")
                .sort_values(by="TOTAL", ascending=False)
                .head(10)
            )
            fig_top_crimes_upd = px.bar(
                top_crimes_upd.sort_values("TOTAL"),
                x="TOTAL",
                y="NATUREZA_APURADA",
                color="NATUREZA_APURADA",
                orientation="h",
                title="10 Tipos de Crime Mais Frequentes",
                labels={"TOTAL": "Quantidade", "NATUREZA_APURADA": "Natureza"},
                color_discrete_map=CRIME_COLOR_MAP
            )
            fig_top_crimes_upd.update_layout(
                title_x=0.5,
                yaxis={"categoryorder": "total ascending"},
                showlegend=False
            )

            # 2. Distribuição Relativa de Crimes por Porte
            df_porte_filtered = df_enriched.copy()
            if cidade_selecionada:
                df_porte_filtered = df_porte_filtered[df_porte_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
            if dia_selecionado:
                df_porte_filtered = df_porte_filtered[df_porte_filtered["DIA_SEMANA"] == dia_selecionado]
            if porte_selecionado:
                df_porte_filtered = df_porte_filtered[df_porte_filtered["PORTE_MUNICIPIO"] == porte_selecionado]

            df_porte_upd = (
                df_porte_filtered
                .groupby(["PORTE_MUNICIPIO", "NATUREZA_APURADA"])
                .size()
                .reset_index(name="TOTAL")
            )
            fig_natureza_porte_upd = px.bar(
                df_porte_upd,
                x="TOTAL",
                y="PORTE_MUNICIPIO",
                color="NATUREZA_APURADA",
                orientation="h",
                title="Distribuição Relativa de Crimes por Porte do Município",
                labels={
                    "PORTE_MUNICIPIO": "Porte do Município",
                    "TOTAL": "Proporção",
                    "NATUREZA_APURADA": "Natureza"
                },
                color_discrete_map=CRIME_COLOR_MAP
            )
            fig_natureza_porte_upd.update_layout(
                title_x=0.5,
                title_font=dict(size=16, family="Arial, sans-serif"),
                barmode="stack",
                barnorm="percent",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=180, r=30, t=50, b=50),
                xaxis=dict(ticksuffix="%")
            )
            fig_natureza_porte_upd.update_traces(hovertemplate="<b>%{hovertext}</b><br>Proporção: %{x:.2f}%<extra></extra>")

            # 3. Natureza dos Crimes por Dia da Semana (Heatmap)
            df_heatmap_filtered = df_enriched.copy()
            if porte_selecionado:
                df_heatmap_filtered = df_heatmap_filtered[df_heatmap_filtered["PORTE_MUNICIPIO"] == porte_selecionado]
            if cidade_selecionada:
                df_heatmap_filtered = df_heatmap_filtered[df_heatmap_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
            if dia_selecionado:
                df_heatmap_filtered = df_heatmap_filtered[df_heatmap_filtered["DIA_SEMANA"] == dia_selecionado]

            heatmap_data_upd = (
                df_heatmap_filtered
                .groupby(["NATUREZA_APURADA", "DIA_SEMANA"])
                .size()
                .reset_index(name="TOTAL")
                .pivot_table(
                    index="NATUREZA_APURADA",
                    columns="DIA_SEMANA",
                    values="TOTAL",
                    aggfunc="sum"
                )
                .fillna(0)
            )

            cols_ord_heatmap = [d for d in ordem_dias if d in heatmap_data_upd.columns]
            if cols_ord_heatmap:
                heatmap_data_upd = heatmap_data_upd[cols_ord_heatmap]

            fig_heatmap_upd = px.imshow(
                heatmap_data_upd,
                aspect="auto",
                title="Tipos de Crime por Dia da Semana",
                labels={
                    "x": "Dia da Semana",
                    "y": "Natureza do Crime",
                    "color": "Ocorrências"
                },
                color_continuous_scale="Reds"
            )
            fig_heatmap_upd.update_layout(
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
            fig_heatmap_upd.update_yaxes(tickfont=dict(size=11))

            # 4. Sunburst
            df_sun_filtered = df_enriched.copy()
            if porte_selecionado:
                df_sun_filtered = df_sun_filtered[df_sun_filtered["PORTE_MUNICIPIO"] == porte_selecionado]
            if cidade_selecionada:
                df_sun_filtered = df_sun_filtered[df_sun_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
            if dia_selecionado:
                df_sun_filtered = df_sun_filtered[df_sun_filtered["DIA_SEMANA"] == dia_selecionado]

            sun_agg = (
                df_sun_filtered
                .groupby(["NOME_MUNICIPIO", "NATUREZA_APURADA"])
                .size()
                .reset_index(name="TOTAL")
                .sort_values("TOTAL", ascending=False)
            )

            if not cidade_selecionada:
                top_cidades_upd = (
                    sun_agg
                    .groupby("NOME_MUNICIPIO")["TOTAL"]
                    .sum()
                    .nlargest(10)
                    .index
                )
                sun_filtrado = sun_agg[
                    sun_agg["NOME_MUNICIPIO"].isin(top_cidades_upd)
                ]
                title_sun = "Categorias de Crime por Cidade (Top 10)"
            else:
                sun_filtrado = sun_agg
                title_sun = f"Categorias de Crime em {cidade_selecionada}"

            fig_sunburst_upd = px.treemap(
                sun_filtrado,
                path=["NOME_MUNICIPIO", "NATUREZA_APURADA"],
                values="TOTAL",
                color="NATUREZA_APURADA",
                color_discrete_map=CRIME_COLOR_MAP,
                title=title_sun
            )
            fig_sunburst_upd.update_layout(
                title_x=0.5,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            fig_sunburst_upd.update_traces(
                textinfo="label+value+percent parent",
                hovertemplate="<b>%{label}</b><br>Ocorrências: %{value:,}<br>% da cidade: %{percentParent:.1%}<extra></extra>"
            )

            # 5. Heatmap Grupo por Dia da Semana
            df_gsemana_filtered = df_enriched.copy()
            if porte_selecionado:
                df_gsemana_filtered = df_gsemana_filtered[df_gsemana_filtered["PORTE_MUNICIPIO"] == porte_selecionado]
            if cidade_selecionada:
                df_gsemana_filtered = df_gsemana_filtered[df_gsemana_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
            if dia_selecionado:
                df_gsemana_filtered = df_gsemana_filtered[df_gsemana_filtered["DIA_SEMANA"] == dia_selecionado]

            grupo_semana_pivot_upd = (
                df_gsemana_filtered
                .groupby(["GRUPO", "DIA_SEMANA"])
                .size()
                .reset_index(name="TOTAL")
                .pivot_table(
                    index="GRUPO",
                    columns="DIA_SEMANA",
                    values="TOTAL",
                    aggfunc="sum"
                )
                .fillna(0)
            )

            cols_ord_gsemana = [d for d in ordem_dias if d in grupo_semana_pivot_upd.columns]
            if cols_ord_gsemana:
                grupo_semana_pivot_upd = grupo_semana_pivot_upd[cols_ord_gsemana]

            fig_grupo_heatmap_upd = px.imshow(
                grupo_semana_pivot_upd,
                aspect="auto",
                title="Intensidade: Grupo de Crime por Dia da Semana",
                labels={
                    "x": "Dia da Semana",
                    "y": "Grupo",
                    "color": "Ocorrências"
                },
                color_continuous_scale="Reds"
            )
            fig_grupo_heatmap_upd.update_layout(
                title_x=0.5,
                title_font=dict(size=16, family="Arial, sans-serif"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=150, r=20, t=50, b=50)
            )

            # 6. Faixa Horária
            df_gfaixa_filtered = df_enriched.copy()
            if porte_selecionado:
                df_gfaixa_filtered = df_gfaixa_filtered[df_gfaixa_filtered["PORTE_MUNICIPIO"] == porte_selecionado]
            if cidade_selecionada:
                df_gfaixa_filtered = df_gfaixa_filtered[df_gfaixa_filtered["NOME_MUNICIPIO"] == cidade_selecionada]
            if dia_selecionado:
                df_gfaixa_filtered = df_gfaixa_filtered[df_gfaixa_filtered["DIA_SEMANA"] == dia_selecionado]

            if "FAIXA_HORARIA" in df_gfaixa_filtered.columns:
                df_gfaixa_filtered = df_gfaixa_filtered[df_gfaixa_filtered["FAIXA_HORARIA"] != "Indefinido"]

            df_gfaixa_agg = (
                df_gfaixa_filtered
                .groupby(["FAIXA_HORARIA", "GRUPO"])
                .size()
                .reset_index(name="TOTAL")
            )

            fig_faixa_upd = px.bar(
                df_gfaixa_agg,
                x="FAIXA_HORARIA",
                y="TOTAL",
                color="GRUPO",
                title="Distribuição por Faixa Horária e Grupo",
                labels={
                    "FAIXA_HORARIA": "Faixa Horária",
                    "TOTAL": "Ocorrências",
                    "GRUPO": "Grupo"
                },
                category_orders={"FAIXA_HORARIA": ordem_faixas}
            )
            fig_faixa_upd.update_layout(
                title_x=0.5,
                barmode="stack"
            )

            return (
                fig_top_crimes_upd,
                fig_natureza_porte_upd,
                fig_heatmap_upd,
                fig_sunburst_upd,
                fig_grupo_heatmap_upd,
                fig_faixa_upd
            )
        else:
            df_porte = natureza_porte.copy()
            df_semana = natureza_semana.copy()
            df_sun = sunburst_data.copy()
            df_gsemana = grupo_semana.copy()
            df_gfaixa = grupo_faixa.copy()

            if cidade_selecionada and df_enriched is not None:
                municipios_filtrados = df_enriched[
                    df_enriched["NOME_MUNICIPIO"] == cidade_selecionada
                ]
                naturezas_cidade = municipios_filtrados["NATUREZA_APURADA"].unique()
                portes_cidade = municipios_filtrados["PORTE_MUNICIPIO"].unique()
                grupos_cidade = municipios_filtrados["GRUPO"].unique()

                df_porte = df_porte[
                    df_porte["NATUREZA_APURADA"].isin(naturezas_cidade)
                    & df_porte["PORTE_MUNICIPIO"].isin(portes_cidade)
                ]
                df_semana = df_semana[
                    df_semana["NATUREZA_APURADA"].isin(naturezas_cidade)
                ]
                df_sun = df_sun[
                    df_sun["NOME_MUNICIPIO"] == cidade_selecionada
                ]
                df_gsemana = df_gsemana[
                    df_gsemana["GRUPO"].isin(grupos_cidade)
                ]
                df_gfaixa = df_gfaixa[
                    df_gfaixa["GRUPO"].isin(grupos_cidade)
                ]

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

            if dia_selecionado:
                df_semana_filtrada = df_semana[
                    df_semana["DIA_SEMANA"] == dia_selecionado
                ]
                df_gsemana = df_gsemana[
                    df_gsemana["DIA_SEMANA"] == dia_selecionado
                ]
            else:
                df_semana_filtrada = df_semana

            top_crimes_upd = (
                df_porte
                .groupby("NATUREZA_APURADA")["TOTAL"]
                .sum()
                .reset_index()
                .sort_values(by="TOTAL", ascending=False)
                .head(10)
            )

            fig_top_crimes_upd = px.bar(
                top_crimes_upd.sort_values("TOTAL"),
                x="TOTAL",
                y="NATUREZA_APURADA",
                color="NATUREZA_APURADA",
                orientation="h",
                title="10 Tipos de Crime Mais Frequentes",
                color_discrete_map=CRIME_COLOR_MAP
            )
            fig_top_crimes_upd.update_layout(
                showlegend=False
            )

            fig_natureza_porte_upd = px.bar(
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
                },
                color_discrete_map=CRIME_COLOR_MAP
            )

            fig_natureza_porte_upd.update_layout(
                title_x=0.5,
                title_font=dict(size=16, family="Arial, sans-serif"),
                barmode="stack",
                barnorm="percent",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=180, r=30, t=50, b=50),
                xaxis=dict(ticksuffix="%")
            )
            fig_natureza_porte_upd.update_traces(hovertemplate="<b>%{hovertext}</b><br>Proporção: %{x:.2f}%<extra></extra>")

            heatmap_data_upd = (
                df_semana_filtrada
                .pivot_table(
                    index="NATUREZA_APURADA",
                    columns="DIA_SEMANA",
                    values="TOTAL",
                    aggfunc="sum"
                )
                .fillna(0)
            )

            fig_heatmap_upd = px.imshow(
                heatmap_data_upd,
                aspect="auto",
                title="Tipos de Crime por Dia da Semana",
                labels={
                    "x": "Dia da Semana",
                    "y": "Natureza do Crime",
                    "color": "Ocorrências"
                },
                color_continuous_scale="Reds"
            )

            fig_heatmap_upd.update_layout(
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
            fig_heatmap_upd.update_yaxes(tickfont=dict(size=11))

            sun_top = df_sun.sort_values("TOTAL", ascending=False)
            top_cidades_upd = (
                sun_top
                .groupby("NOME_MUNICIPIO")["TOTAL"]
                .sum()
                .nlargest(10)
                .index
            )
            sun_filtrado = sun_top[
                sun_top["NOME_MUNICIPIO"].isin(top_cidades_upd)
            ]

            fig_sunburst_upd = px.treemap(
                sun_filtrado,
                path=["NOME_MUNICIPIO", "NATUREZA_APURADA"],
                values="TOTAL",
                color="NATUREZA_APURADA",
                color_discrete_map=CRIME_COLOR_MAP,
                title="Categorias de Crime por Cidade (Top 10)"
            )
            fig_sunburst_upd.update_layout(
                title_x=0.5,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            fig_sunburst_upd.update_traces(
                textinfo="label+value+percent parent",
                hovertemplate="<b>%{label}</b><br>Ocorrências: %{value:,}<br>% da cidade: %{percentParent:.1%}<extra></extra>"
            )

            grupo_semana_pivot_upd = (
                df_gsemana
                .pivot_table(
                    index="GRUPO",
                    columns="DIA_SEMANA",
                    values="TOTAL",
                    aggfunc="sum"
                )
                .fillna(0)
            )

            cols_ord = [d for d in ordem_dias if d in grupo_semana_pivot_upd.columns]
            if cols_ord:
                grupo_semana_pivot_upd = grupo_semana_pivot_upd[cols_ord]

            fig_grupo_heatmap_upd = px.imshow(
                grupo_semana_pivot_upd,
                aspect="auto",
                title="Intensidade: Grupo de Crime por Dia da Semana",
                labels={
                    "x": "Dia da Semana",
                    "y": "Grupo",
                    "color": "Ocorrências"
                },
                color_continuous_scale="Reds"
            )

            fig_grupo_heatmap_upd.update_layout(
                title_x=0.5,
                title_font=dict(size=16, family="Arial, sans-serif"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=150, r=20, t=50, b=50)
            )

            fig_faixa_upd = px.bar(
                df_gfaixa,
                x="FAIXA_HORARIA",
                y="TOTAL",
                color="GRUPO",
                title="Distribuição por Faixa Horária e Grupo",
                labels={
                    "FAIXA_HORARIA": "Faixa Horária",
                    "TOTAL": "Ocorrências",
                    "GRUPO": "Grupo"
                },
                category_orders={"FAIXA_HORARIA": ordem_faixas}
            )

            fig_faixa_upd.update_layout(
                title_x=0.5,
                barmode="stack"
            )

            return (
                fig_top_crimes_upd,
                fig_natureza_porte_upd,
                fig_heatmap_upd,
                fig_sunburst_upd,
                fig_grupo_heatmap_upd,
                fig_faixa_upd
            )

    return app