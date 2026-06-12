"""
pages/dashboard2.py — Dashboard 2: Exploração Interativa
"""

import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_store

dash.register_page(__name__, path="/explorar", name="Exploração Interativa", order=1)

C = {
    "bg":      "#0a0e1a",
    "card":    "#111827",
    "border":  "#1e293b",
    "text":    "#f1f5f9",
    "sub":     "#94a3b8",
    "muted":   "#475569",
    "accent":  "#6366f1",
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

ORDEM_MESES = ["Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
MESES = {7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

PLOT_BASE = dict(
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
    df       = data_store.df_global
    municipios = sorted(df["NOME_MUNICIPIO"].dropna().unique().tolist())
    grupos     = sorted(df["GRUPO_CRIME"].dropna().unique().tolist())
    faixas     = [f for f in ["Madrugada (00h–05h)","Manhã (06h–11h)",
                               "Tarde (12h–17h)","Noite (18h–23h)"]
                  if f in df["FAIXA_HORARIA"].unique()]

    return html.Div([
        # Header
        html.Div([
            html.H1("Exploração Interativa",
                    style={"margin":0,"fontSize":"1.5rem","fontWeight":"700","color":C["text"]}),
            html.P("Use os filtros para explorar os dados em detalhe",
                   style={"margin":0,"color":C["sub"],"fontSize":"0.82rem","marginTop":"4px"}),
        ], className="dash-header"),

        # Filtros
        html.Div([
            html.Div([
                html.Label("Município", className="filter-label"),
                dcc.Dropdown(
                    id="f-municipio",
                    options=[{"label": m.title(), "value": m} for m in municipios[:50]],
                    multi=True, placeholder="Todos os municípios...",
                    className="dash-dropdown",
                ),
            ], className="filter-item"),

            html.Div([
                html.Label("Grupo de Crime", className="filter-label"),
                dcc.Dropdown(
                    id="f-grupo",
                    options=[{"label": g, "value": g} for g in grupos],
                    multi=True, placeholder="Todos os grupos...",
                    className="dash-dropdown",
                ),
            ], className="filter-item"),

            html.Div([
                html.Label("Período (Meses)", className="filter-label"),
                dcc.RangeSlider(
                    id="f-mes", min=7, max=12, step=1,
                    marks={m: {"label": MESES[m][:3],
                               "style": {"color": C["sub"], "fontSize": "11px"}}
                           for m in range(7, 13)},
                    value=[7, 12],
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ], className="filter-item filter-slider"),

            html.Div([
                html.Label("Faixa Horária", className="filter-label"),
                dcc.Dropdown(
                    id="f-hora",
                    options=[{"label": f, "value": f} for f in faixas],
                    multi=True, placeholder="Todas as faixas...",
                    className="dash-dropdown",
                ),
            ], className="filter-item"),
        ], className="filters-panel"),

        # Badge de registros
        html.Div(id="badge-registros", className="records-badge"),

        # G1: Série temporal
        html.Div([
            html.Div([dcc.Graph(id="g-temporal", config={"displayModeBar":False},
                                style={"height":"340px"})],
                     className="chart-card chart-full"),
        ], className="charts-row"),

        # G2 + G3
        html.Div([
            html.Div([dcc.Graph(id="g-heatmap", config={"displayModeBar":False},
                                style={"height":"360px"})],
                     className="chart-card"),
            html.Div([dcc.Graph(id="g-municipios", config={"displayModeBar":False},
                                style={"height":"360px"})],
                     className="chart-card"),
        ], className="charts-row-equal"),

        # G4 + G5
        html.Div([
            html.Div([dcc.Graph(id="g-treemap", config={"displayModeBar":False},
                                style={"height":"380px"})],
                     className="chart-card"),
            html.Div([dcc.Graph(id="g-local", config={"displayModeBar":False},
                                style={"height":"380px"})],
                     className="chart-card"),
        ], className="charts-row-equal"),

        # G6: Scatter per capita
        html.Div([
            html.Div([dcc.Graph(id="g-percapita", config={"displayModeBar":False},
                                style={"height":"400px"})],
                     className="chart-card chart-full"),
        ], className="charts-row"),

    ], className="page-content")


def _filtrar(municipios, grupos, meses, horas):
    df = data_store.df_global.copy()
    if municipios:  df = df[df["NOME_MUNICIPIO"].isin(municipios)]
    if grupos:      df = df[df["GRUPO_CRIME"].isin(grupos)]
    if meses:       df = df[df["MES_ESTATISTICA"].between(meses[0], meses[1])]
    if horas:       df = df[df["FAIXA_HORARIA"].isin(horas)]
    return df


def _vazio():
    fig = go.Figure()
    fig.add_annotation(text="Nenhum dado para os filtros selecionados",
                       xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font=dict(color=C["sub"], size=13))
    fig.update_layout(**PLOT_BASE)
    return fig


@callback(
    Output("badge-registros", "children"),
    Output("g-temporal",  "figure"),
    Output("g-heatmap",   "figure"),
    Output("g-municipios","figure"),
    Output("g-treemap",   "figure"),
    Output("g-local",     "figure"),
    Output("g-percapita", "figure"),
    Input("f-municipio",  "value"),
    Input("f-grupo",      "value"),
    Input("f-mes",        "value"),
    Input("f-hora",       "value"),
)
def atualizar(municipios, grupos, meses, horas):
    df = _filtrar(municipios, grupos, meses, horas)
    total_geral = len(data_store.df_global)

    if len(df) == 0:
        badge = "0 registros selecionados"
        v = _vazio()
        return badge, v, v, v, v, v, v

    badge = html.Span([
        html.Strong(f"{len(df):,}", style={"color": C["accent"]}),
        f" de {total_geral:,} ocorrências selecionadas",
    ])

    # ── G1 Série temporal ─────────────────────────────────────────────
    df_mes = (df.groupby(["MES_NOME","GRUPO_CRIME"], observed=True)
                .size().reset_index(name="T"))
    df_mes["ORD"] = pd.Categorical(df_mes["MES_NOME"], categories=ORDEM_MESES, ordered=True)
    df_mes = df_mes.sort_values("ORD")

    fig_t = go.Figure()
    for g in df_mes["GRUPO_CRIME"].unique():
        sub = df_mes[df_mes["GRUPO_CRIME"] == g]
        fig_t.add_trace(go.Scatter(
            x=sub["MES_NOME"], y=sub["T"], name=g,
            mode="lines+markers",
            line=dict(color=GRUPO_COLOR.get(g, C["muted"]), width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{g}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>",
        ))
    fig_t.update_layout(title=_titulo("Evolução Mensal por Grupo de Crime"), **PLOT_BASE)

    # ── G2 Heatmap dia × hora ─────────────────────────────────────────
    dias_ord  = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    horas_ord = ["Madrugada (00h–05h)","Manhã (06h–11h)","Tarde (12h–17h)","Noite (18h–23h)"]

    df_h = (df[df["FAIXA_HORARIA"].isin(horas_ord)]
              .groupby(["DIA_SEMANA","FAIXA_HORARIA"], observed=True)
              .size().reset_index(name="T"))

    pivot = df_h.pivot_table(index="FAIXA_HORARIA", columns="DIA_SEMANA",
                             values="T", fill_value=0)
    dias_p = [d for d in dias_ord if d in pivot.columns]
    hor_p  = [h for h in horas_ord if h in pivot.index]
    pivot  = pivot.reindex(columns=dias_p, index=hor_p, fill_value=0)

    fig_h = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0,"#0d1117"],[0.4,"#312e81"],[1,"#6366f1"]],
        text=[[f"{v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f}<extra></extra>",
        showscale=False,
    ))
    fig_h.update_layout(title=_titulo("Ocorrências: Dia × Faixa Horária"), **PLOT_BASE)

    # ── G3 Barras empilhadas municípios ───────────────────────────────
    top8 = df["NOME_MUNICIPIO"].value_counts().head(8).index.tolist()
    df_m = (df[df["NOME_MUNICIPIO"].isin(top8)]
              .groupby(["NOME_MUNICIPIO","GRUPO_CRIME"], observed=True)
              .size().reset_index(name="T"))
    df_m["NOME_MUNICIPIO"] = df_m["NOME_MUNICIPIO"].str.title()

    fig_m = go.Figure()
    for g in df_m["GRUPO_CRIME"].unique():
        sub = df_m[df_m["GRUPO_CRIME"] == g]
        fig_m.add_trace(go.Bar(
            name=g, x=sub["NOME_MUNICIPIO"], y=sub["T"],
            marker_color=GRUPO_COLOR.get(g, C["muted"]),
            hovertemplate=f"<b>{g}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>",
        ))
    fig_m.update_layout(barmode="stack",
                        title=_titulo("Top 8 Municípios por Grupo de Crime"),
                        **PLOT_BASE)

    # ── G4 Treemap ────────────────────────────────────────────────────
    top12 = df["NOME_MUNICIPIO"].value_counts().head(12).index.tolist()
    df_tr = (df[df["NOME_MUNICIPIO"].isin(top12)]
               .groupby(["NOME_MUNICIPIO","GRUPO_CRIME"], observed=True)
               .size().reset_index(name="T"))
    df_tr["NOME_MUNICIPIO"] = df_tr["NOME_MUNICIPIO"].str.title()

    fig_tr = px.treemap(df_tr, path=["NOME_MUNICIPIO","GRUPO_CRIME"], values="T",
                        color="GRUPO_CRIME",
                        color_discrete_map={**GRUPO_COLOR, "(?)": C["border"]})
    fig_tr.update_traces(
        textinfo="label+value",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    )
    fig_tr.update_layout(title=_titulo("Hierarquia: Município → Tipo de Crime"),
                         paper_bgcolor=C["plot_bg"],
                         font=dict(color=C["sub"], family="Inter"),
                         margin=dict(l=10, r=10, t=40, b=10))

    # ── G5 Tipo de local ──────────────────────────────────────────────
    df_lc = (df[df["DESCR_TIPOLOCAL"].str.upper() != "NÃO INFORMADO"]
               .groupby("DESCR_TIPOLOCAL", observed=True)
               .size().reset_index(name="T")
               .sort_values("T", ascending=False).head(9))
    df_lc["DESCR_TIPOLOCAL"] = df_lc["DESCR_TIPOLOCAL"].str.title()

    fig_lc = go.Figure(go.Bar(
        x=df_lc["T"], y=df_lc["DESCR_TIPOLOCAL"],
        orientation="h",
        marker=dict(color=C["accent"], opacity=0.75),
        text=df_lc["T"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(color=C["sub"], size=10),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig_lc.update_layout(title=_titulo("Crimes por Tipo de Local"), **PLOT_BASE)
    fig_lc.update_yaxes(autorange="reversed")

    # ── G6 Scatter per capita ─────────────────────────────────────────
    df_pc = (df.groupby("NOME_MUNICIPIO", observed=True)
               .agg(T=("RUBRICA","count"), POP=("POPULACAO_ESTIMADA","first"))
               .reset_index())
    df_pc = df_pc[df_pc["POP"] > 10_000]
    df_pc["TAXA"] = (df_pc["T"] / df_pc["POP"]) * 100_000
    df_pc["NOME_MUNICIPIO"] = df_pc["NOME_MUNICIPIO"].str.title()
    top10_names = df_pc.nlargest(10, "T")["NOME_MUNICIPIO"].tolist()

    fig_pc = go.Figure()
    outros = df_pc[~df_pc["NOME_MUNICIPIO"].isin(top10_names)]
    fig_pc.add_trace(go.Scatter(
        x=outros["POP"], y=outros["TAXA"],
        mode="markers",
        name="Demais municípios",
        marker=dict(size=5, color=C["muted"], opacity=0.6),
        text=outros["NOME_MUNICIPIO"],
        hovertemplate="<b>%{text}</b><br>Pop: %{x:,.0f}<br>Taxa/100k: %{y:.1f}<extra></extra>",
    ))
    top_df = df_pc[df_pc["NOME_MUNICIPIO"].isin(top10_names)]
    fig_pc.add_trace(go.Scatter(
        x=top_df["POP"], y=top_df["TAXA"],
        mode="markers+text",
        name="Top 10",
        marker=dict(size=12, color=C["accent"],
                    line=dict(color=C["text"], width=1)),
        text=top_df["NOME_MUNICIPIO"],
        textposition="top center",
        textfont=dict(size=9, color=C["text"]),
        hovertemplate="<b>%{text}</b><br>Pop: %{x:,.0f}<br>Taxa/100k: %{y:.1f}<extra></extra>",
    ))
    lyt = {**PLOT_BASE}
    lyt["xaxis"] = dict(title="População (IBGE 2025)", type="log",
                        gridcolor=C["grid"], tickfont=dict(size=10),
                        title_font=dict(color=C["sub"]))
    lyt["yaxis"] = dict(title="Crimes por 100k hab.",
                        gridcolor=C["grid"], tickfont=dict(size=10),
                        title_font=dict(color=C["sub"]))
    fig_pc.update_layout(title=_titulo("Taxa de Crimes por 100k Habitantes × População"), **lyt)

    return badge, fig_t, fig_h, fig_m, fig_tr, fig_lc, fig_pc
