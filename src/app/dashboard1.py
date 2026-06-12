import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
        xaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"], tickfont=dict(size=9, color=c["sec"])),
        yaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"], tickfont=dict(size=9, color=c["sec"])),
    )

def layout(df: pd.DataFrame) -> html.Div:
    total_crimes = len(df)
    municipio_top = df["NOME_MUNICIPIO"].value_counts().idxmax() if not df.empty else "N/A"
    
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Total de Ocorrências", className="kpi-title"),
                            html.Div(f"{total_crimes:,}".replace(",", "."), className="kpi-value"),
                            html.Div("Base Consolidada Jul a Dez de 2025", className="kpi-sub"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Maior Volume Absoluto", className="kpi-title"),
                            html.Div(str(municipio_top).upper(), className="kpi-value-small"),
                            html.Div("Município com mais registros brutos", className="kpi-sub"),
                        ],
                        className="kpi-card",
                    ),
                ],
                className="kpis-container",
            ),
            html.Div(style={"height": "20px"}),
            html.Div(
                [
                    html.Div(id="chart-top10-wrapper", className="chart-card"),
                    html.Div(id="chart-porte-wrapper", className="chart-card"),
                ],
                className="charts-row charts-row-2",
            ),
        ],
        className="main-content",
    )

def register_callbacks(app, dict_datasets: dict):

    @app.callback(
        Output("chart-top10-wrapper", "children"),
        Output("chart-porte-wrapper", "children"),
        Input("current-theme", "data"),
    )
    def update_d1_charts(theme):
        theme = theme or "dark"
        c = _colors(theme)
        
        # Gráfico 1: Top 10 Cidades Violentas
        df_top = dict_datasets.get("top_10_cidades", pd.DataFrame())
        if df_top.empty:
            g1_children = [html.Div("Sem dados para o Top 10", className="chart-card-subtitle")]
        else:
            fig_top = px.bar(
                df_top, x="TAXA_CRIMES_100K", y="NOME_MUNICIPIO",
                orientation="h", color="TAXA_CRIMES_100K",
                color_continuous_scale="Reds"
            )
            fig_top.update_layout(**_base(c, margin=dict(l=150, r=20, t=20, b=40)), coloraxis_showscale=False)
            fig_top.update_yaxes(autorange="reversed")
            g1_children = [
                html.Div("Top 10 Municípios por Taxa (100k hab.)", className="chart-card-title"),
                dcc.Graph(figure=fig_top, config={"displayModeBar": False}, style={"height": "350px"})
            ]

        # Gráfico 2: Distribuição por Porte
        df_porte = dict_datasets.get("distribuicao_porte", pd.DataFrame())
        if df_porte.empty:
            g2_children = [html.Div("Sem dados para Distribuição por Porte", className="chart-card-subtitle")]
        else:
            fig_porte = px.pie(
                df_porte, names="PORTE_MUNICIPIO", values="TOTAL_CRIMES",
                color_discrete_sequence=["#3b82f6", "#f59e0b", "#dc2626"]
            )
            fig_porte.update_layout(
                paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
                font=dict(family="Inter", size=10, color=c["text"]),
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", y=-0.1, x=0, font=dict(size=9, color=c["text"]))
            )
            g2_children = [
                html.Div("Volume Total de Crimes por Porte de Município", className="chart-card-title"),
                dcc.Graph(figure=fig_porte, config={"displayModeBar": False}, style={"height": "350px"})
            ]
            
        return g1_children, g2_children