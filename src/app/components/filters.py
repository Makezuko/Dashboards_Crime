from dash import html, dcc


# ── Paleta de cores dos gráficos Plotly ──────────────────────────────────────

PLOTLY_COLORS = {
    "Furto":          "#f59e0b",
    "Roubo":          "#ef4444",
    "Lesão Corporal": "#f97316",
    "Trânsito":       "#3b82f6",
    "Drogas":         "#8b5cf6",
    "Crimes Sexuais": "#ec4899",
    "Homicídio":      "#dc2626",
    "Armas":          "#06b6d4",
    "Outros":         "#6b7280",
}

COLOR_SEQUENCE = list(PLOTLY_COLORS.values())


# ── Funções de layout de gráfico Plotly ──────────────────────────────────────

def plotly_layout(theme: str = "dark", title: str = "") -> dict:
    """
    Retorna um dicionário de layout Plotly compatível com o tema ativo.
    theme: 'dark' | 'mid' | 'light'
    """
    bg_map = {
        "dark":  {"plot": "#161d2e", "paper": "#161d2e", "grid": "rgba(255,255,255,0.06)", "text": "#f9fafb", "secondary": "#9ca3af"},
        "mid":   {"plot": "#2a3a52", "paper": "#2a3a52", "grid": "rgba(255,255,255,0.08)", "text": "#f1f5f9", "secondary": "#94a3b8"},
        "light": {"plot": "#ffffff", "paper": "#ffffff", "grid": "rgba(0,0,0,0.08)",       "text": "#0f172a", "secondary": "#334155"},
    }
    c = bg_map.get(theme, bg_map["dark"])

    return dict(
        title=dict(text=title, font=dict(size=13, color=c["text"], family="Inter"), x=0, xanchor="left", pad=dict(b=10)),
        paper_bgcolor=c["paper"],
        plot_bgcolor=c["plot"],
        font=dict(family="Inter", size=11, color=c["text"]),
        xaxis=dict(
            gridcolor=c["grid"], zerolinecolor=c["grid"],
            tickfont=dict(size=10, color=c["secondary"]),
            linecolor=c["grid"],
        ),
        yaxis=dict(
            gridcolor=c["grid"], zerolinecolor=c["grid"],
            tickfont=dict(size=10, color=c["secondary"]),
            linecolor=c["grid"],
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=c["grid"],
            font=dict(size=10, color=c["text"]),
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        margin=dict(l=50, r=20, t=40, b=50),
        hoverlabel=dict(
            bgcolor=c["plot"],
            bordercolor=c["grid"],
            font=dict(size=11, color=c["text"], family="Inter"),
        ),
    )


# ── KPI Card ─────────────────────────────────────────────────────────────────

def kpi_card(card_id: str, label: str, value: str, subtitle: str = "",
             color: str = "blue", badge: str = "") -> html.Div:
    """Card de KPI com barra de cor no topo."""
    children = [
        html.Div(label, className="kpi-label"),
        html.Div(value, className="kpi-value" + (" small" if len(str(value)) > 12 else "")),
    ]
    if badge:
        children.append(html.Span(badge, className="kpi-badge"))
    if subtitle:
        children.append(html.Div(subtitle, className="kpi-subtitle"))

    return html.Div(
        children,
        id=card_id,
        className=f"kpi-card color-{color}",
    )


# ── Chart Card wrapper ────────────────────────────────────────────────────────

def chart_card(title: str, subtitle: str, children, insight_tag: str = "",
               insight_color: str = "blue", callout: str = "") -> html.Div:
    """Wrapper visual para um gráfico com título, subtítulo e callout opcional."""
    header = []
    if insight_tag:
        header.append(html.Div(insight_tag, className=f"insight-tag {insight_color}"))
    header += [
        html.Div(title, className="chart-card-title"),
        html.Div(subtitle, className="chart-card-subtitle"),
    ]

    footer = []
    if callout:
        footer.append(html.Div(callout, className=f"insight-callout {insight_color}"))

    return html.Div(
        header + [children] + footer,
        className="chart-card",
    )


# ── Section Title ─────────────────────────────────────────────────────────────

def section_title(title: str, subtitle: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(title, className="section-title"),
            html.Div(subtitle, className="section-subtitle") if subtitle else None,
        ],
        className="section-header",
    )


# ── Theme Toggle ─────────────────────────────────────────────────────────────

def theme_toggle() -> html.Div:
    return html.Div(
        [
            html.Button("Escuro", id="theme-btn-dark",  className="theme-btn active", n_clicks=0),
            html.Button("Medio",  id="theme-btn-mid",   className="theme-btn",        n_clicks=0),
            html.Button("Claro",  id="theme-btn-light", className="theme-btn",        n_clicks=0),
        ],
        className="theme-toggle-group",
    )


# ── Navbar ────────────────────────────────────────────────────────────────────

def navbar(active_tab: str = "d1") -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Criminalidade SP", className="navbar-brand-text"),
                    html.Div("Jul–Dez 2025 | Estado de São Paulo", className="navbar-brand-sub"),
                ]
            ),
            html.Div(
                [theme_toggle()],
                className="navbar-right",
            ),
        ],
        className="navbar-custom",
    )


def tab_bar(active: str = "d1") -> html.Div:
    return html.Div(
        [
            html.Button(
                "Visao Geral",
                id="tab-d1",
                className=f"tab-link {'active' if active == 'd1' else ''}",
                n_clicks=0,
            ),
            html.Button(
                "Exploracao Interativa",
                id="tab-d2",
                className=f"tab-link {'active' if active == 'd2' else ''}",
                n_clicks=0,
            ),
        ],
        className="tab-bar",
    )


# ── Filtros do Dashboard 2 ────────────────────────────────────────────────────

GRUPOS_OPCOES = [
    {"label": "Furto",          "value": "Furto"},
    {"label": "Roubo",          "value": "Roubo"},
    {"label": "Lesao Corporal", "value": "Lesão Corporal"},
    {"label": "Transito",       "value": "Trânsito"},
    {"label": "Drogas",         "value": "Drogas"},
    {"label": "Crimes Sexuais", "value": "Crimes Sexuais"},
    {"label": "Homicidio",      "value": "Homicídio"},
    {"label": "Armas",          "value": "Armas"},
]

MESES_OPCOES = [
    {"label": "Julho",    "value": "Julho"},
    {"label": "Agosto",   "value": "Agosto"},
    {"label": "Setembro", "value": "Setembro"},
    {"label": "Outubro",  "value": "Outubro"},
    {"label": "Novembro", "value": "Novembro"},
    {"label": "Dezembro", "value": "Dezembro"},
]

FAIXA_OPCOES = [
    {"label": "Madrugada (00h–05h)", "value": "Madrugada (00h–05h)"},
    {"label": "Manha (06h–11h)",     "value": "Manhã (06h–11h)"},
    {"label": "Tarde (12h–17h)",     "value": "Tarde (12h–17h)"},
    {"label": "Noite (18h–23h)",     "value": "Noite (18h–23h)"},
]


def sidebar_filters(municipios_opcoes: list) -> html.Div:
    return html.Div(
        [
            html.Div("Filtros", className="sidebar-title"),

            # Filtro 1: Grupo de crime
            html.Div(
                [
                    html.Label("Grupo de Crime", className="filter-label"),
                    dcc.Dropdown(
                        id="filter-grupo",
                        options=GRUPOS_OPCOES,
                        value=[],
                        multi=True,
                        placeholder="Todos os grupos...",
                        clearable=True,
                        style={"fontSize": "0.8rem"},
                    ),
                ],
                className="filter-group",
            ),

            # Filtro 2: Município
            html.Div(
                [
                    html.Label("Municipio", className="filter-label"),
                    dcc.Dropdown(
                        id="filter-municipio",
                        options=municipios_opcoes,
                        value=[],
                        multi=True,
                        placeholder="Todos os municipios...",
                        clearable=True,
                        style={"fontSize": "0.8rem"},
                    ),
                ],
                className="filter-group",
            ),

            # Filtro 3: Mês
            html.Div(
                [
                    html.Label("Mes", className="filter-label"),
                    dcc.Checklist(
                        id="filter-mes",
                        options=MESES_OPCOES,
                        value=[m["value"] for m in MESES_OPCOES],
                        className="dash-checklist",
                        labelStyle={"display": "flex"},
                    ),
                ],
                className="filter-group",
            ),

            # Filtro 4: Faixa horária
            html.Div(
                [
                    html.Label("Faixa Horaria", className="filter-label"),
                    dcc.Checklist(
                        id="filter-faixa",
                        options=FAIXA_OPCOES,
                        value=[f["value"] for f in FAIXA_OPCOES],
                        className="dash-checklist",
                        labelStyle={"display": "flex"},
                    ),
                ],
                className="filter-group",
            ),

            html.Button(
                "Limpar Filtros",
                id="btn-reset-filters",
                className="btn-reset",
                n_clicks=0,
            ),
        ],
        className="sidebar",
    )