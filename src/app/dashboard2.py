import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

ORDEM_DIAS = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]


def _colors(theme):
    return {
        "dark":  dict(bg="#161d2e", text="#f9fafb", sec="#9ca3af", grid="rgba(255,255,255,0.06)"),
        "mid":   dict(bg="#2a3a52", text="#f1f5f9", sec="#94a3b8", grid="rgba(255,255,255,0.08)"),
        "light": dict(bg="#ffffff", text="#0f172a", sec="#334155", grid="rgba(0,0,0,0.08)"),
    }.get(theme, {})


def _base(c, margin=None):
    m = margin or dict(l=50, r=20, t=30, b=50)
    return dict(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        font=dict(family="Inter", size=10, color=c["text"]),
        margin=m,
        hoverlabel=dict(bgcolor=c["bg"], font=dict(size=10, color=c["text"], family="Inter")),
        xaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"], tickfont=dict(size=9, color=c["sec"])),
        yaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"], tickfont=dict(size=9, color=c["sec"])),
    )


def layout(df: pd.DataFrame) -> html.Div:
    from src.app.components.filters import sidebar_filters
    
    mun_options = [{"label": m, "value": m} for m in sorted(df["NOME_MUNICIPIO"].unique())[:40]]

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Exploração Interativa", className="section-title"),
                    html.Div(
                        "Análise de criminalidade baseada no porte do município, densidade demográfica e perfil semanal",
                        className="section-subtitle",
                    ),
                ],
                className="section-header",
            ),
            html.Div(
                [
                    sidebar_filters(mun_options),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(id="d2-heatmap-card", className="chart-card"),
                                    html.Div(id="d2-sunburst-card", className="chart-card"),
                                ],
                                className="charts-row charts-row-2",
                            ),
                            html.Div(style={"height": "20px"}),
                            html.Div(
                                [
                                    html.Div(id="d2-monthly-card", className="chart-card"),
                                    html.Div(id="d2-homrate-card", className="chart-card"),
                                ],
                                className="charts-row charts-row-2",
                            ),
                            html.Div(style={"height": "20px"}),
                            html.Div(
                                [
                                    html.Div(id="d2-bubble-card", className="chart-card"),
                                    html.Div(id="d2-hourly-card", className="chart-card"),
                                ],
                                className="charts-row charts-row-2",
                            ),
                        ],
                        className="charts-area",
                    ),
                ],
                className="d2-layout",
            ),
            html.Div(style={"height": "32px"}),
        ],
        className="main-content",
    )


def register_callbacks(app, dict_datasets: dict):

    @app.callback(
        Output("d2-heatmap-card",  "children"),
        Output("d2-sunburst-card", "children"),
        Output("d2-monthly-card",  "children"),
        Output("d2-homrate-card",  "children"),
        Output("d2-bubble-card",   "children"),
        Output("d2-hourly-card",   "children"),
        Input("filter-grupo",      "value"),
        Input("filter-municipio",  "value"),
        Input("filter-mes",        "value"),
        Input("filter-faixa",      "value"),
        Input("current-theme",     "data"),
    )
    def update_d2_charts(grupos, municipios, meses, faixas, theme):
        theme = theme or "dark"
        c = _colors(theme)
        _empty = lambda: [html.Div("Sem dados para os filtros selecionados.", className="chart-card-subtitle")]

        # 1. Perfil Semanal (Heatmap alternativo via Barras por conta do formato do df_semanal)
        df_semanal = dict_datasets.get("perfil_semanal", pd.DataFrame()).copy()
        if municipios:
            df_semanal = df_semanal[df_semanal["NOME_MUNICIPIO"].isin(municipios)]
            
        if df_semanal.empty:
            heatmap_card = _empty()
        else:
            df_semanal_agg = df_semanal.groupby("DIA_SEMANA", observed=True)["TOTAL_CRIMES"].sum().reset_index()
            fig_heat = px.bar(
                df_semanal_agg, x="DIA_SEMANA", y="TOTAL_CRIMES",
                category_orders={"DIA_SEMANA": ORDEM_DIAS},
                color_discrete_sequence=["#3b82f6"]
            )
            fig_heat.update_layout(**_base(c, margin=dict(l=60, r=20, t=30, b=50)), yaxis_title="Total Crimes", xaxis_title="")
            heatmap_card = [
                html.Div("Volume de Crimes por Dia da Semana", className="chart-card-title"),
                html.Div("Distribuição temporal ao longo da semana", className="chart-card-subtitle"),
                dcc.Graph(figure=fig_heat, config={"displayModeBar": False}, style={"height": "310px"}),
            ]

        # 2. Distribuição por Porte (Substituindo Sunburst pela agregação real do pipeline)
        df_porte = dict_datasets.get("distribuicao_porte", pd.DataFrame())
        if df_porte.empty:
            sunburst_card = _empty()
        else:
            fig_sun = px.pie(
                df_porte, names="PORTE_MUNICIPIO", values="TOTAL_CRIMES",
                color_discrete_sequence=["#3b82f6", "#f59e0b", "#dc2626"]
            )
            fig_sun.update_traces(texttemplate="%{percent:.1%}", textfont=dict(size=11, family="Inter"))
            fig_sun.update_layout(
                paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
                font=dict(family="Inter", size=10, color=c["text"]),
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", y=-0.1, x=0, font=dict(size=9, color=c["text"]))
            )
            sunburst_card = [
                html.Div("Proporção de Crimes por Porte do Município", className="chart-card-title"),
                html.Div("Percentual acumulado por faixa populacional", className="chart-card-subtitle"),
                dcc.Graph(figure=fig_sun, config={"displayModeBar": False}, style={"height": "310px"}),
            ]

        # 3. Evolução Mensal (Construído a partir do df_base enriquecido se necessário, usando os dados agregados de correlação)
        df_corr = dict_datasets.get("correlacao_densidade", pd.DataFrame()).copy()
        if municipios:
            df_corr = df_corr[df_corr["NOME_MUNICIPIO"].isin(municipios)]

        if df_corr.empty:
            monthly_card = _empty()
        else:
            df_natureza = df_corr.groupby("NATUREZA_APURADA")["TOTAL_CRIMES"].sum().reset_index()
            df_natureza = df_natureza.sort_values(by="TOTAL_CRIMES", ascending=False).head(10)
            fig_mon = px.bar(
                df_natureza, x="TOTAL_CRIMES", y="NATUREZA_APURADA",
                orientation="h", color_discrete_sequence=["#10b981"]
            )
            fig_mon.update_layout(**_base(c, margin=dict(l=180, r=20, t=30, b=50)), xaxis_title="Ocorrências", yaxis_title="")
            monthly_card = [
                html.Div("Top 10 Naturezas de Crime Apuradas", className="chart-card-title"),
                html.Div("Volume total das principais tipificações encontradas", className="chart-card-subtitle"),
                dcc.Graph(figure=fig_mon, config={"displayModeBar": False}, style={"height": "310px"}),
            ]

        # 4. Top Cidades Violentas (Insight A)
        df_top_10 = dict_datasets.get("top_10_cidades", pd.DataFrame())
        if df_top_10.empty:
            homrate_card = _empty()
        else:
            fig_hom = go.Figure(
                go.Bar(
                    x=df_top_10["TAXA_CRIMES_100K"], y=df_top_10["NOME_MUNICIPIO"],
                    orientation="h", marker_color="#dc2626",
                    text=df_top_10["TAXA_CRIMES_100K"].apply(lambda v: f"{v:.1f}"),
                    textposition="outside", textfont=dict(size=9, color=c["text"]),
                )
            )
            fig_hom.update_layout(**_base(c, margin=dict(l=160, r=70, t=30, b=30)), xaxis_title="Taxa por 100k hab.")
            fig_hom.update_yaxes(autorange="reversed")
            homrate_card = [
                html.Div("Insight A", className="insight-tag red"),
                html.Div("Taxa Geral de Crimes — Top 10 Municípios", className="chart-card-title"),
                html.Div("Ranking com base na taxa proporcional por 100 mil habitantes", className="chart-card-subtitle"),
                dcc.Graph(figure=fig_hom, config={"displayModeBar": False}, style={"height": "310px"}),
            ]

        # 5. Bubble Chart: Densidade x Volume
        if df_corr.empty:
            bubble_card = _empty()
        else:
            df_bubble_agg = df_corr.groupby(["NOME_MUNICIPIO", "DENSIDADE_DEMOGRAFICA", "POPULACAO"])["TOTAL_CRIMES"].sum().reset_index()
            fig_bub = px.scatter(
                df_bubble_agg, x="DENSIDADE_DEMOGRAFICA", y="TOTAL_CRIMES", size="POPULACAO",
                hover_name="NOME_MUNICIPIO", size_max=30,
                color="DENSIDADE_DEMOGRAFICA",
                color_continuous_scale=[[0, "#3b82f6"], [0.5, "#f59e0b"], [1, "#dc2626"]],
            )
            fig_bub.update_traces(marker=dict(opacity=0.7))
            fig_bub.update_layout(
                **_base(c, margin=dict(l=60, r=20, t=30, b=50)),
                xaxis_title="Densidade Demográfica", yaxis_title="Total de Crimes",
                coloraxis_colorbar=dict(thickness=10, len=0.85, tickfont=dict(size=9, color=c["text"])),
            )
            bubble_card = [
                html.Div("Correlação: Densidade Demográfica vs Volume", className="chart-card-title"),
                html.Div("Tamanho da bolha representa o tamanho da população", className="chart-card-subtitle"),
                dcc.Graph(figure=fig_bub, config={"displayModeBar": False}, style={"height": "320px"}),
            ]

        # 6. Gráfico de Fallback (Vazio/Informativo já que o pipeline não computou faixa horária)
        hourly_card = [
            html.Div("Distribuição por Faixa Horária", className="chart-card-title"),
            html.Div("Módulo não implementado no pipeline de transformação atual", className="chart-card-subtitle"),
            html.Div("Os dados brutos não possuem a feature de hora tratada.", className="insight-callout amber")
        ]

        return heatmap_card, sunburst_card, monthly_card, homrate_card, bubble_card, hourly_card

    @app.callback(
        Output("filter-grupo",      "value"),
        Output("filter-municipio", "value"),
        Output("filter-mes",       "value"),
        Output("filter-faixa",     "value"),
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_):
        return [], [], [], []