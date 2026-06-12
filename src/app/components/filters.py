from dash import html, dcc


def create_filters():

    return html.Div([

        html.Div([

            html.Label("Ano"),

            dcc.Dropdown(
                id="ano",
                options=[
                    {"label": "2019", "value": 2019},
                    {"label": "2020", "value": 2020}
                ],
                placeholder="Selecione"
            )

        ], className="filter"),

        html.Div([

            html.Label("Município"),

            dcc.Dropdown(
                id="municipio",
                placeholder="Selecione"
            )

        ], className="filter")

    ], className="filters-container")