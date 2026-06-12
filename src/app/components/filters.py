from dash import html, dcc


def create_filters(natureza_porte, natureza_semana):

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

        ], className="filter")

    ], className="filters-container")
