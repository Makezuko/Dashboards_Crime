import requests
import pandas as pd
import urllib3
import json

urllib3.disable_warnings()

print("Baixando dados populacionais IBGE Tabela 6579 - SP 2025...")

url = "http://api.sidra.ibge.gov.br/values/t/6579/n6/in%20n3%2035/v/9324/p/2025?formato=json"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, verify=False)
print("Status:", r.status_code)

data = r.json()
header_row = data[0]
rows = data[1:]

print("Header keys:", list(header_row.keys()))
print("Header values:", list(header_row.values()))
print("Primeiro dado:", rows[0])

df = pd.DataFrame(rows, columns=list(header_row.keys()))
print("Columns do df:", list(df.columns))
print("Shape:", df.shape)

# Rename using actual column names from header
rename_map = {}
for k, v in header_row.items():
    if "digo" in v and "Municipal" in v or k == "D1C":
        rename_map[k] = "COD_IBGE"
    elif k == "D1N":
        rename_map[k] = "MUNICIPIO_IBGE"
    elif k == "V":
        rename_map[k] = "POPULACAO_ESTIMADA"
    elif k == "D3N":
        rename_map[k] = "ANO"

print("Rename map:", rename_map)
df = df.rename(columns=rename_map)

df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")
df["MUNICIPIO_NOME"] = df["MUNICIPIO_IBGE"].str.replace(" - SP", "").str.strip()

cols = ["COD_IBGE", "MUNICIPIO_IBGE", "MUNICIPIO_NOME", "POPULACAO_ESTIMADA", "ANO"]
cols_exist = [c for c in cols if c in df.columns]
df_final = df[cols_exist].copy()

print("\nShape final:", df_final.shape)
print(df_final.head(5).to_string())
print("\nTotal municipios:", len(df_final))
print("Populacao total SP:", "{:,.0f}".format(df_final["POPULACAO_ESTIMADA"].sum()))

out = "dados/populacao_municipios_SP_2025.csv"
df_final.to_csv(out, index=False, encoding="utf-8-sig")
print("Salvo em:", out)
