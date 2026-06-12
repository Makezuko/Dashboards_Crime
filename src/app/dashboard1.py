import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

def init_dashboard(dash_app, dict_datasets_dash):
    df_top10 = dict_datasets_dash["top_10_cidades"]
    df_porte = dict_datasets_dash["distribuicao_porte"]
    df_corr = dict_datasets_dash["correlacao_densidade"]
    df_semana = dict_datasets_dash["perfil_semanal"]
    df_nat_porte = dict_datasets_dash["natureza_porte"]

    total_crimes_global = int(df_porte["TOTAL_CRIMES"].sum())
    total_crimes_formatado = f"{total_crimes_global:,}".replace(",", ".")

    df_porte_pct = df_porte.copy()
    df_porte_pct["PERCENTUAL"] = (df_porte_pct["TOTAL_CRIMES"] / total_crimes_global) * 100
    
    pct_grande_porte = 0.0
    grande_porte_rows = df_porte_pct[df_porte_pct["PORTE_MUNICIPIO"].str.contains("GRANDE")]
    if not grande_porte_rows.empty:
        pct_grande_porte = grande_porte_rows.iloc[0]["PERCENTUAL"]

    cidade_maior_taxa = "N/A"
    maior_taxa_valor = 0.0
    cidade_maior_pop = 0
    if not df_top10.empty:
        cidade_maior_taxa = df_top10.iloc[0]["NOME_MUNICIPIO"]
        maior_taxa_valor = df_top10.iloc[0]["TAXA_CRIMES_100K"]
        cidade_maior_pop = int(df_top10.iloc[0]["POPULACAO"])
    maior_taxa_formatada = f"{maior_taxa_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    crime_dominante = "N/A"
    if not df_nat_porte.empty:
        crime_dominante = df_nat_porte.groupby("NATUREZA_APURADA")["TOTAL"].sum().idxmax()

    correlacao_geral = df_corr["DENSIDADE_DEMOGRAFICA"].corr(df_corr["TAXA_CRIMES_100K"])
    status_corr = "forte" if abs(correlacao_geral) > 0.7 else "moderada" if abs(correlacao_geral) > 0.4 else "fraca ou inexistente"

    df_dias_agg = df_semana.groupby("DIA_SEMANA", observed=True)["TOTAL_CRIMES"].sum().reset_index()
    df_dias_agg["PERCENTUAL"] = (df_dias_agg["TOTAL_CRIMES"] / total_crimes_global) * 100
    
    dia_pico = "N/A"
    pct_pico = 0.0
    if not df_dias_agg.empty:
        idx_pico = df_dias_agg["TOTAL_CRIMES"].idxmax()
        dia_pico = df_dias_agg.loc[idx_pico, "DIA_SEMANA"]
        pct_pico = df_dias_agg.loc[idx_pico, "PERCENTUAL"]

    fig_temporal = go.Figure()
    fig_temporal.add_trace(go.Bar(
        x=df_dias_agg["DIA_SEMANA"],
        y=df_dias_agg["TOTAL_CRIMES"],
        marker_color=['#dc2626' if dia == dia_pico else '#3b82f6' for dia in df_dias_agg["DIA_SEMANA"]]
    ))
    fig_temporal.update_layout(
        title=f'Volume de Crimes por Dia da Semana (Pico: {dia_pico})',
        template='plotly_white',
        margin=dict(l=40, r=20, t=60, b=40),
        height=350,
        font=dict(color='#1f2937') # Cor escura
    )
    fig_porte = go.Figure(data=[go.Pie(
        labels=df_porte_pct["PORTE_MUNICIPIO"],
        values=df_porte_pct["TOTAL_CRIMES"],
        hole=.4,
        marker=dict(colors=['#3b82f6', '#06b6d4', '#8b5cf6'])
    )])
    
    fig_porte.update_layout(
        title='Distribuição Absoluta por Porte de Município',
        template='plotly_white',
        margin=dict(l=20, r=20, t=60, b=40),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#1f2937')),
        font=dict(color='#1f2937') # Cor escura
    )

    dash_app.layout = html.Div(className="dashboard-container", children=[
        
        html.Div(className="header-container", children=[
            html.H1("Painel Executivo de Segurança Pública", className="dashboard-title"),
            html.P("Visão Geral Semestral, Indicadores Críticos e Insights Estocásticos", className="dashboard-subtitle")
        ]),
        
        html.Div(className="grid-cards", children=[
            
            html.Div(className="card card-total", children=[
                html.H6("TOTAL DE OCORRÊNCIAS", className="card-title"),
                html.H2(total_crimes_formatado, className="card-value"),
                html.P(f"Concentração de {pct_grande_porte:.2f}% em Grandes Centros", className="card-subtext subtext-total")
            ]),
            
            html.Div(className="card card-taxa", children=[
                html.H6("MAIOR TAXA (POR 100K HAB)", className="card-title"),
                html.H2(maior_taxa_formatada, className="card-value card-value-taxa"),
                html.P(f"{cidade_maior_taxa} (Pop: {cidade_maior_pop})", className="card-subtext subtext-taxa")
            ]),
            
            html.Div(className="card card-dominante", children=[
                html.H6("CRIME DOMINANTE GLOBAL", className="card-title"),
                html.H2(crime_dominante.title(), className="card-value-dominante"),
                html.P("Líder absoluto em volume", className="card-subtext subtext-dominante")
            ]),
            
            html.Div(className="card card-densidade", children=[
                html.H6("DENSIDADE VS CRIMINALIDADE", className="card-title"),
                html.H2(f"{correlacao_geral:.4f}".replace(".", ","), className="card-value"),
                html.P(f"Correlação {status_corr}", className="card-subtext subtext-densidade")
            ])
        ]),
        
        html.Div(className="grid-charts", children=[
            html.Div(className="chart-wrapper", children=[
                dcc.Graph(figure=fig_temporal, config={'displayModeBar': False})
            ]),
            html.Div(className="chart-wrapper", children=[
                dcc.Graph(figure=fig_porte, config={'displayModeBar': False})
            ])
        ]),
        
        html.Div(className="insights-container", children=[
            html.H4("Análise Estratégica e Achados Geográficos", className="insights-title"),
            
            html.Div(className="insights-grid-cards", children=[
                
                html.Div(className="insight-card", children=[
                    html.Div(className="insight-badge badge-temporal", children="Comportamento Temporal"),
                    html.H5(f"Dinâmica Semanal e Pico de Ocorrências às {dia_pico.title()}s"),
                    html.P([
                        f"O volume de crimes distribui-se de forma relativamente homogênea entre os dias úteis, mas apresenta um pico claro às {dia_pico.lower()}s ({pct_pico:.2f}% / {df_dias_agg['TOTAL_CRIMES'].max():,} casos) e uma queda acentuada aos domingos. No acumulado do fim de semana, os crimes mais frequentes migram para padrões específicos como 'Furto - Outros', 'Roubo - Outros' e 'Lesão Corporal Dolosa'."
                    ], className="insight-text-main"),
                    html.P([
                        f"A sexta-feira funciona como o dia de transição para o fim de semana, com maior circulação de pessoas, transações financeiras e atividades de lazer noturno, o que eleva as oportunidades para a prática de crimes patrimoniais. Paralelamente, a alta de 'Lesão Corporal Dolosa' nos fins de semana aponta para conflitos interpessoais atrelados a momentos de socialização. Essa dinâmica justifica o planejamento de escalas operacionais diferenciadas, com reforço de policiamento ostensivo preventivo direcionado a partir das tardes de sexta-feira."
                    ], className="insight-text-context")
                ]),
                
                html.Div(className="insight-card", children=[
                    html.Div(className="insight-badge badge-paradoxo", children="Análise de Grupos"),
                    html.H5("O Paradoxo Demográfico: Volume Absoluto vs. Proporcional"),
                    html.P([
                        f"Existe uma disparidade crítica quando analisamos os municípios de forma absoluta versus proporcional. Em volume total, as cidades de Grande Porte detêm a concentração majoritária de {pct_grande_porte:.2f}% de todos os registros do estado ({df_porte_pct[df_porte_pct['PORTE_MUNICIPIO'].str.contains('GRANDE')]['TOTAL_CRIMES'].sum():,} casos). No entanto, o Top 10 de localidades mais violentas por taxa por 100k habitantes é ocupado por municípios pequenos como {cidade_maior_taxa} ({maior_taxa_formatada} por 100k) e Rifaina, além de estâncias litorâneas e turísticas."
                    ], className="insight-text-main"),
                    html.P([
                        "Esse padrão decorre de duas dinâmicas distintas: a distorção estatística natural de pequenas populações (onde poucos eventos inflam bruscamente as taxas per capita) e o impacto da população flutuante em regiões turísticas, que acolhem milhares de pessoas não recenseadas mas geram ocorrências locais. O fenômeno da interiorização da violência se confirma de forma qualificada: o volume bruto permanece urbano-metropolitano, mas a severidade per capita afeta o interior e o litoral de forma desproporcional à população residente."
                    ], className="insight-text-context")
                ]),
                
                html.Div(className="insight-card", children=[
                    html.Div(className="insight-badge badge-variaveis", children="Métricas Correlatas"),
                    html.H5("A Desmistificação da Densidade Urbana como Vetor"),
                    html.P([
                        f"O coeficiente de correlação linear entre a Densidade Demográfica e a Taxa de Crimes apresentou um índice residual praticamente zerado ({correlacao_geral:.4f}), estabelecendo uma relação {status_corr}. Em contrapartida, as naturezas criminais que pontuaram com maior taxa média por densidade foram 'Homicídio Culposo Outros' (2,77), 'Porte de Entorpecentes' (2,40) e 'Roubo a Banco' (2,05)."
                    ], className="insight-text-main"),
                    html.P([
                        "Este achado contraria o senso comum de que cidades densamente povoadas são linearmente mais violentas. A densidade isolada não se comporta como um preditor de criminalidade. Municípios com grandes extensões territoriais e baixa densidade média sofrem com criminalidade severa pulverizada, enquanto áreas compactas podem conter bolsões de segurança eficientes. O fato de crimes complexos como 'Roubo a Banco' e sinistros de trânsito severos pontuarem alto reforça que as manchas criminais complexas independem do adensamento das calçadas."
                    ], className="insight-text-context")
                ]),
                
                html.Div(className="insight-card", children=[
                    html.Div(className="insight-badge badge-perfil", children="Tipificação Local"),
                    html.H5("Variação Teórica das Naturezas por Porte de Município"),
                    html.P([
                        f"Embora o '{crime_dominante}' figure como o crime líder absoluto em volume em todas as categorias de porte (registrando {df_nat_porte[df_nat_porte['NATUREZA_APURADA']==crime_dominante]['TOTAL'].sum():,} casos totais), as segundas e terceiras posições na mancha criminal variam drasticamente conforme o tamanho da cidade. Nos grandes centros urbanos, o foco é marcadamente patrimonial violento (Roubo e Furto de Veículos), ao passo que nos municípios médios e pequenos a relevância migra para delitos de trânsito e conflitos interpessoais."
                    ], className="insight-text-main"),
                    html.P([
                        "Nas metrópoles, a atividade criminal mostra-se mais profissionalizada, organizada e integrada a mercados clandestinos de receptação de veículos e eletrônicos. No interior, embora os furtos ordinários aconteçam, as demandas locais de segurança pública são estatisticamente infladas por ocorrências de 'Lesão Corporal Dolosa' (atritos cotidianos) e 'Lesão Culposa por Trânsito'. Isso exige uma mudança de postura do Estado, aplicando estratégias de mediação comunitária e engenharia viária nessas localidades, em vez do modelo padrão de policiamento metropolitano."
                    ], className="insight-text-context")
                ])
                
            ])
        ])
    ])
    return dash_app