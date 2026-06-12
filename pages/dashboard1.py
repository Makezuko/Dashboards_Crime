"""
pages/dashboard1.py — Dashboard 1: Visão Geral Executiva
"""

import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_store

dash.register_page(__name__, path="/", name="Visão Geral", order=0)

# ── Paleta discreta (menos colorida) ──────────────────────────
C = {
    "bg":      "#0a0e1a",
    "card":    "#111827",
    "border":  "#1e293b",
    "text":    "#f1f5f9",
    "sub":     "#94a3b8",
    "muted":   "#475569",
    "accent":  "#6366f1",   # apenas 1 cor de destaque
    "plot_bg": "#111827",
    "grid":    "#1e293b",
}

GRUPO_COLOR = {
    "Furto":          "#6366f1",
    "Trânsito":       "#64748b",
    "Lesão Corporal": "#475569",
    "Roubo":          "#818cf8",
    "Drogas":         "#a5b4fc",
    "Homicídio":      "#ef4444",
    "Crimes Sexuais": "#f87171",
    "Armas":          "#94a3b8",
    "Outros":         "#334155",
}

PLOT = dict(
    paper_bgcolor=C["plot_bg"],
    plot_bgcolor=C["plot_bg"],
    font=dict(color=C["sub"], family="Inter"),
    margin=dict(l=12, r=20, t=40, b=10),
    xaxis=dict(gridcolor=C["grid"], zeroline=False, tickfont=dict(size=10)),
    yaxis=dict(gridcolor=C["grid"], zeroline=False, tickfont=dict(size=10)),
    hoverlabel=dict(bgcolor="#1e293b", font=dict(color=C["text"], size=12)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=C["sub"])),
)


def _titulo(t):
    return dict(text=t, font=dict(size=13, color=C["sub"], family="Inter"),
                x=0, pad=dict(l=0, t=0))


def layout():
    df      = data_store.df_global
    df_g    = data_store.df_grupos
    df_muns = data_store.df_top_muns
    df_loc  = data_store.df_local

    total        = len(df)
    crime_top    = df["RUBRICA"].value_counts().index[0]
    crime_top_n  = df["RUBRICA"].value_counts().iloc[0]
    cidade_top   = df["NOME_MUNICIPIO"].value_counts().index[0].title()
    cidade_top_n = df["NOME_MUNICIPIO"].value_counts().iloc[0]
    meses_nome   = {7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    mes_top      = meses_nome.get(int(df["MES_ESTATISTICA"].value_counts().index[0]), "—")
    homicidios   = len(df[df["GRUPO_CRIME"] == "Homicídio"])

    ORDEM = ["Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

    # ── G1 Linha mensal ───────────────────────────────────────────────
    df_mes = df.groupby("MES_NOME").size().reset_index(name="TOTAL")
    df_mes["ORD"] = pd.Categorical(df_mes["MES_NOME"], categories=ORDEM, ordered=True)
    df_mes = df_mes.sort_values("ORD")

    fig_linha = go.Figure(go.Scatter(
        x=df_mes["MES_NOME"], y=df_mes["TOTAL"],
        mode="lines+markers+text",
        text=df_mes["TOTAL"].apply(lambda x: f"{x:,.0f}"),
        textposition="top center",
        textfont=dict(size=10, color=C["text"]),
        line=dict(color=C["accent"], width=2.5),
        marker=dict(size=8, color=C["accent"]),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.06)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} ocorrências<extra></extra>",
    ))
    fig_linha.update_layout(title=_titulo("Evolução Mensal de Ocorrências"), **PLOT)

    # ── G2 Barras horizontais top crimes ──────────────────────────────
    top_rub = df["RUBRICA"].value_counts().head(10).reset_index()
    top_rub.columns = ["CRIME","TOTAL"]
    top_rub["CRIME"] = top_rub["CRIME"].str.title().str[:50]

    fig_bar = go.Figure(go.Bar(
        x=top_rub["TOTAL"], y=top_rub["CRIME"],
        orientation="h",
        marker=dict(color=C["accent"], opacity=0.85),
        text=top_rub["TOTAL"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(color=C["sub"], size=10),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig_bar.update_layout(title=_titulo("Top 10 Tipos de Crime"), **PLOT)
    fig_bar.update_yaxes(autorange="reversed")

    # ── G3 Donut grupos ────────────────────────────────────────────────
    df_gp = df_g.copy()
    cores = [GRUPO_COLOR.get(g, C["muted"]) for g in df_gp["GRUPO_CRIME"]]

    fig_donut = go.Figure(go.Pie(
        labels=df_gp["GRUPO_CRIME"], values=df_gp["TOTAL"],
        hole=0.58,
        marker=dict(colors=cores, line=dict(color=C["bg"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:11px'>total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=15, color=C["text"]),
    )
    fig_donut.update_layout(title=_titulo("Por Grupo de Crime"), **PLOT)

    # ── G4 Top municípios ──────────────────────────────────────────────
    top10 = df_muns.head(10).copy()
    top10["NOME_MUNICIPIO"] = top10["NOME_MUNICIPIO"].str.title()

    fig_muns = go.Figure(go.Bar(
        x=top10["TOTAL"], y=top10["NOME_MUNICIPIO"],
        orientation="h",
        marker=dict(color=C["accent"], opacity=0.75),
        text=top10["TOTAL"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(color=C["sub"], size=10),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig_muns.update_layout(title=_titulo("Top 10 Municípios"), **PLOT)
    fig_muns.update_yaxes(autorange="reversed")

    # ── G5 Tipo de local ──────────────────────────────────────────────
    df_lc = df_loc[df_loc["DESCR_TIPOLOCAL"].str.upper() != "NÃO INFORMADO"].head(8).copy()
    df_lc["DESCR_TIPOLOCAL"] = df_lc["DESCR_TIPOLOCAL"].str.title()

    fig_local = go.Figure(go.Bar(
        x=df_lc["TOTAL"], y=df_lc["DESCR_TIPOLOCAL"],
        orientation="h",
        marker=dict(color=C["accent"], opacity=0.6),
        text=df_lc["TOTAL"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(color=C["sub"], size=10),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig_local.update_layout(title=_titulo("Crimes por Tipo de Local"), **PLOT)
    fig_local.update_yaxes(autorange="reversed")

    return html.Div([
        # ── Header ──────────────────────────────────────────────────
        html.Div([
            html.H1("Visão Geral",
                    style={"margin":0,"fontSize":"1.5rem","fontWeight":"700","color":C["text"]}),
            html.P("Dados Criminais — Estado de São Paulo | Jul–Dez 2025 | SSP-SP + IBGE",
                   style={"margin":0,"color":C["sub"],"fontSize":"0.82rem","marginTop":"4px"}),
        ], className="dash-header"),

        # ── KPI Cards ────────────────────────────────────────────────
        html.Div([
            _kpi("Total de Ocorrências",    f"{total:,}",        "Jul–Dez 2025"),
            _kpi("Crime Mais Frequente",    crime_top.split("(")[0].strip().title()[:30],
                                             f"{crime_top_n:,} casos"),
            _kpi("Município Mais Afetado",  cidade_top,           f"{cidade_top_n:,} ocorrências"),
            _kpi("Mês com Mais Casos",      mes_top,              "Período analisado"),
            _kpi("Homicídios Registrados",  f"{homicidios:,}",   "Período completo"),
        ], className="kpi-row"),

        # ── Linha 1: evolução + donut ────────────────────────────────
        html.Div([
            html.Div([dcc.Graph(figure=fig_linha,
                                config={"displayModeBar":False}, style={"height":"320px"})],
                     className="chart-card chart-wide"),
            html.Div([dcc.Graph(figure=fig_donut,
                                config={"displayModeBar":False}, style={"height":"320px"})],
                     className="chart-card chart-narrow"),
        ], className="charts-row"),

        # ── Linha 2: top crimes + municípios ────────────────────────
        html.Div([
            html.Div([dcc.Graph(figure=fig_bar,
                                config={"displayModeBar":False}, style={"height":"380px"})],
                     className="chart-card"),
            html.Div([dcc.Graph(figure=fig_muns,
                                config={"displayModeBar":False}, style={"height":"380px"})],
                     className="chart-card"),
        ], className="charts-row-equal"),

        # ── Linha 3: tipo de local ───────────────────────────────────
        html.Div([
            html.Div([dcc.Graph(figure=fig_local,
                                config={"displayModeBar":False}, style={"height":"320px"})],
                     className="chart-card chart-full"),
        ], className="charts-row"),

        # ── Insights ─────────────────────────────────────────────────
        html.Div([
            html.H3("Principais Insights",
                    style={"color":C["text"],"fontSize":"1rem","marginBottom":"14px",
                           "fontWeight":"600"}),
            html.Div([
                _insight("Furto domina",
                    f"Furtos representam {df_g[df_g['GRUPO_CRIME']=='Furto']['TOTAL'].sum():,.0f} ocorrências "
                    f"({df_g[df_g['GRUPO_CRIME']=='Furto']['TOTAL'].sum()/total*100:.1f}% do total), "
                    "sendo o crime mais prevalente em todas as regiões do estado."),
                _insight("Concentração em SP capital",
                    f"São Paulo capital concentra {cidade_top_n:,} ocorrências "
                    f"({cidade_top_n/total*100:.1f}% do total estadual), proporcional à sua densidade populacional."),
                _insight("Violência no trânsito",
                    f"Crimes relacionados ao trânsito somam "
                    f"{df_g[df_g['GRUPO_CRIME']=='Trânsito']['TOTAL'].sum():,.0f} casos, "
                    "evidenciando a importância de políticas de segurança viária."),
                _insight("Via pública como epicentro",
                    "A maioria dos crimes ocorre em vias públicas, sugerindo que "
                    "patrulhamento ostensivo e iluminação urbana têm potencial de impacto direto."),
            ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px"}),
        ], className="insight-box"),

    ], className="page-content")


def _kpi(title, value, subtitle):
    return html.Div([
        html.Div(value, className="kpi-value"),
        html.Div(title,   className="kpi-title"),
        html.Div(subtitle, className="kpi-sub"),
    ], className="kpi-card")


def _insight(titulo, texto):
    return html.Div([
        html.Strong(titulo, style={"color":C["text"],"display":"block","marginBottom":"4px"}),
        html.P(texto, style={"color":C["sub"],"fontSize":"0.82rem","margin":0,"lineHeight":"1.55"}),
    ], style={"background":"#0d1117","borderRadius":"8px","padding":"14px",
              "border":"1px solid #1e293b"})
