"""
data_store.py — Armazenamento global dos dados processados
============================================================
Módulo central para compartilhar dados entre app.py e as páginas,
evitando imports circulares.
"""

import pandas as pd

# Variáveis globais — preenchidas pelo app.py na inicialização
df_global: pd.DataFrame = None
df_crimes_mes: pd.DataFrame = None
df_top_muns: pd.DataFrame = None
df_grupos: pd.DataFrame = None
df_heatmap: pd.DataFrame = None
df_local: pd.DataFrame = None
