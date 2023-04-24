import warnings
import sys
import os
import csv
from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse


warnings.simplefilter("ignore")


FII = """BCFF11
BRCO11
BRCR11
BTLG11
CPTS11
HGBS11
HGRU11
JSRE11
KFOF11
KNCR11
KNRI11
LVBI11
MALL11
MCCI11
PATL11
PORD11
PVBI11
RBRF11
RBRR11
VILG11
VISC11
XPIN11
XPML11""".splitlines()


def get_df_data(file_path):
    data = pd.read_excel(file_path, engine="openpyxl", sheet_name="Negociação")
    df = pd.DataFrame(data)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("/", "_", regex=False)
    )
    return df.itertuples(name="Ativo", index=False)


def get_dt(row):
    try:
        dt = str(row.data_do_negócio)
        dt = dt[:10]
        if "/" in dt:
            sep = "/"
            dd, mm, yyyy = str(dt).split(sep)[:3]
        elif "-" in dt:
            sep = "-"
            yyyy, mm, dd = str(dt).split(sep)[:3]
        neg_date = date(int(yyyy), int(mm), int(dd))
        return neg_date.isoformat()[:10]
    except:
        print(row.data_do_negócio)
        print(type(row.data_do_negócio))


def compra(consolidado, code, year_month, qtd, price):
    result = {}
    acoes = code.endswith("F") or code.endswith("3") and not code.endswith("11")

    if code not in consolidado.keys():
        consolidado[code] = {
            "qtd": 0,
            "total": 0,
            "acum_val": 0,
            "acum_qtd": 0,
            "imposto": 0,
        }

    consolidado[code]["acum_qtd"] += qtd
    consolidado[code]["acum_val"] += price * qtd

    return {
        "acum_qtd": consolidado[code]["acum_qtd"],
        "acum_val": round(consolidado[code]["acum_val"], 3),
        "medio": round(
            consolidado[code]["acum_val"] / consolidado[code]["acum_qtd"], 3
        ),
    }


def vende(consolidado, code, year_month, qtd, venda_valor_unit):
    qtd = int(qtd)
    result = {}

    valor_medio = consolidado[code]["acum_val"] / consolidado[code]["acum_qtd"]

    resultado = round(qtd * (venda_valor_unit - valor_medio), 3)

    if resultado < 0:
        # prejuizo
        result["prejuizo"] = resultado
    else:
        # lucro
        x = 0.2 if code in FII else 0.15
        result["lucro"] = resultado
        result["imposto"] = round(resultado * x, 3)
    consolidado[code]["acum_qtd"] -= qtd
    consolidado[code]["acum_val"] = consolidado[code]["acum_qtd"] * valor_medio

    result["acum_qtd"] = round(consolidado[code]["acum_qtd"], 3)
    result["acum_val"] = round(consolidado[code]["acum_val"], 3)
    if result["acum_qtd"]:
        result["medio"] = round(result["acum_val"] / result["acum_qtd"], 3)
    return result


def run(folder_path):
    """
    Data do Negócio
    Tipo de Movimentação
    Mercado
    Prazo/Vencimento
    Instituição
    Código de Negociação
    Quantidade
    Preço
    Valor
    """
    assets = {
        True: {},
        False: {},
    }
    vendas = {
        True: set(),
        False: set(),
    }

    for filename in sorted(os.listdir(folder_path)):
        if filename.startswith("nego"):
            file_path = os.path.join(folder_path, filename)
            rows = get_df_data(file_path)
            for row in rows:
                if row.código_de_negociação == "nan":
                    break
                dt = get_dt(row)
                data = {}
                data["dt"] = dt
                data["op"] = row.tipo_de_movimentação
                data["ativo"] = row.código_de_negociação
                data["corretora"] = row.instituição
                data["qtd"] = row.quantidade
                data["price"] = row.preço
                data["total"] = row.valor

                if data["ativo"].endswith("F") and data["ativo"][-2] in ["3", "1"]:
                    data["ativo"] = data["ativo"][:-1]

                k = data["ativo"]

                fii = k in FII
                if row.tipo_de_movimentação == "Venda":
                    vendas[fii].add(k)
                assets[fii][k] = assets[fii].get(k) or {}
                assets[fii][k][dt] = assets[fii][k].get(dt) or []
                assets[fii][k][dt].insert(0, data)

    fieldnames = [
        "dt",
        "op",
        "ativo",
        "qtd",
        "price",
        "total",
        "acum_val",
        "acum_qtd",
        "medio",
        "imposto",
        "lucro",
        "prejuizo",
        "corretora",
    ]

    for x in (True, False):
        prefix = "fii" if x else "xxx"
        with open(f"planilhas/{prefix}_nego_vendas.csv", "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            consolidado = {}
            for k in vendas[x]:
                for dt in sorted(assets[x][k].keys()):
                    rows = assets[x][k][dt]
                    for row in rows:
                        row["imposto"] = 0
                        row["lucro"] = 0
                        row["prejuizo"] = 0
                        row["acum_val"] = 0
                        row["medio"] = 0
                        if row["op"] == "Venda":
                            r = vende(
                                consolidado,
                                row["ativo"],
                                row["dt"][:-3],
                                row["qtd"],
                                row["price"],
                            )
                        else:
                            r = compra(
                                consolidado,
                                row["ativo"],
                                row["dt"][:-3],
                                row["qtd"],
                                row["price"],
                            )
                        row.update(r)

                        row["price"] = str(row["price"]).replace(".", ",")
                        row["total"] = str(row["total"]).replace(".", ",")
                        row["acum_val"] = str(row["acum_val"]).replace(".", ",")
                        row["lucro"] = str(row["lucro"]).replace(".", ",")
                        row["prejuizo"] = str(row["prejuizo"]).replace(".", ",")
                        row["imposto"] = str(row["imposto"]).replace(".", ",")
                        row["medio"] = str(row["medio"]).replace(".", ",")

                        writer.writerow(row)

        with open(f"planilhas/{prefix}_nego_compras.csv", "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for k in assets[x].keys():
                if k not in vendas[x]:
                    for dt in sorted(assets[x][k].keys()):
                        rows = assets[x][k][dt]
                        for row in rows:
                            row["imposto"] = 0
                            row["lucro"] = 0
                            row["prejuizo"] = 0
                            row["acum_val"] = 0
                            row["medio"] = 0
                            r = compra(
                                consolidado,
                                row["ativo"],
                                row["dt"][:-3],
                                row["qtd"],
                                row["price"],
                            )
                            row.update(r)

                            row["price"] = str(row["price"]).replace(".", ",")
                            row["total"] = str(row["total"]).replace(".", ",")
                            row["acum_val"] = str(row["acum_val"]).replace(".", ",")
                            row["lucro"] = str(row["lucro"]).replace(".", ",")
                            row["prejuizo"] = str(row["prejuizo"]).replace(".", ",")
                            row["imposto"] = str(row["imposto"]).replace(".", ",")
                            row["medio"] = str(row["medio"]).replace(".", ",")
                            writer.writerow(row)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
