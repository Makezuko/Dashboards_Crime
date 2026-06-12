"""
app.py — Aplicação Dash Principal
Dashboard Interativo de Análise Criminal — Estado de São Paulo 2025
Fonte dos dados: SSP-SP + IBGE (Tabela 6579)
"""

import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import dash
from dash import dcc, html, Input, Output
import data_store
from data_pipeline import (
    executar_pipeline,
    get_crimes_por_mes,
    get_top_municipios,
    get_crimes_por_grupo,
    get_heatmap_hora_dia,
    get_crimes_por_local,
)

# ─────────────────────────────────────────────
#  Carregar dados no data_store (sem import circular)
# ─────────────────────────────────────────────
print("\n  Inicializando Dashboard Criminal SP 2025...")
data_store.df_global    = executar_pipeline(forcar_reprocessamento=False)
data_store.df_crimes_mes = get_crimes_por_mes(data_store.df_global)
data_store.df_top_muns  = get_top_municipios(data_store.df_global, n=15)
data_store.df_grupos    = get_crimes_por_grupo(data_store.df_global)
data_store.df_heatmap   = get_heatmap_hora_dia(data_store.df_global)
data_store.df_local     = get_crimes_por_local(data_store.df_global)
print(f"  Pronto! {len(data_store.df_global):,} registros carregados.\n")

# ─────────────────────────────────────────────
#  App Dash — carrega páginas DEPOIS dos dados
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "Dashboard de análise criminal do Estado de SP 2025. Fonte: SSP-SP e IBGE."},
        {"charset": "UTF-8"},
    ],
    title="Dashboard Criminal SP 2025",
)
server = app.server

# ─────────────────────────────────────────────
#  Layout
# ─────────────────────────────────────────────
app.layout = html.Div([
    # Navbar
    html.Nav([
        html.A([
            html.Div([
                html.Div("Dashboard Criminal SP", className="navbar-title"),
                html.Div("Estado de São Paulo · Jul–Dez 2025", className="navbar-subtitle"),
            ]),
        ], href="/", className="navbar-brand"),

        html.Div([
            dcc.Link("Visão Geral",    href="/",        id="nav-visao",   className="nav-link-item"),
            dcc.Link("Exploração",     href="/explorar", id="nav-explorar", className="nav-link-item"),
        ], className="nav-links"),

        html.Div([
            html.Span("Fonte: SSP-SP + IBGE SIDRA 6579",
                      style={"color": "#64748b", "fontSize": "0.75rem"}),
        ], style={"marginLeft": "24px"}),
    ], className="navbar"),

    # Conteúdo das páginas
    dash.page_container,

    # Rodapé
    html.Footer([
        html.Span("Dashboard Criminal SP 2025"),
        html.Span(" · Dados públicos: SSP-SP & IBGE · ",
                  style={"color": "#334155"}),
        html.Span("Python + Dash + Plotly", style={"color": "#6366f1"}),
    ], className="footer"),
], style={"minHeight": "100vh", "background": "#0a0e1a"})


# ─────────────────────────────────────────────
#  Callback: nav link ativo
# ─────────────────────────────────────────────
@app.callback(
    Output("nav-visao",    "className"),
    Output("nav-explorar", "className"),
    Input("_pages_location", "pathname"),
)
def atualizar_nav(pathname):
    base   = "nav-link-item"
    active = "nav-link-item active"
    if pathname == "/explorar":
        return base, active
    return active, base


if __name__ == "__main__":
    print("  Acesse: http://127.0.0.1:8050\n")
    app.run(debug=True, host="127.0.0.1", port=8050)
