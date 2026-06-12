from dash import html, dcc


def create_filters(natureza_porte, natureza_semana, df_enriched=None):

    portes = sorted(
        natureza_porte["PORTE_MUNICIPIO"]
        .unique()
    )

    dias = [
        "SEGUNDA",
        "TERÇA",
        "QUARTA",
        "QUINTA",
        "SEXTA",
        "SÁBADO",
        "DOMINGO"
    ]

    cidades = []
    if df_enriched is not None and "NOME_MUNICIPIO" in df_enriched.columns:
        cidades = sorted(
            df_enriched["NOME_MUNICIPIO"]
            .unique()
        )

    return html.Div([

        html.Div([

            html.Label(
                "Porte do Município"
            ),

            dcc.Dropdown(
                id="filtro-porte",
                options=[
                    {
                        "label": porte,
                        "value": porte
                    }
                    for porte in portes
                ],
                placeholder="Todos os portes",
                clearable=True
            )

        ], className="filter"),

        html.Div([

            html.Label(
                "Dia da Semana"
            ),

            dcc.Dropdown(
                id="filtro-dia",
                options=[
                    {
                        "label": dia,
                        "value": dia
                    }
                    for dia in dias
                ],
                placeholder="Todos os dias",
                clearable=True
            )

        ], className="filter"),

        html.Div([

            html.Label(
                "Cidade"
            ),

            dcc.Dropdown(
                id="filtro-cidade",
                options=[
                    {
                        "label": c,
                        "value": c
                    }
                    for c in cidades
                ],
                placeholder="Todas as cidades",
                clearable=True,
                searchable=True
            )

        ], className="filter")

    ], className="filters-container")
