import sys
import os
import csv
from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse


def get_df_data(file_path):
    data = pd.read_excel(file_path, sheet_name="Negociação")
    df = pd.DataFrame(data)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("/", "_")
    )
    return df.itertuples(name="Ativo", index=False)


def compra(assets, code, year_month, qtd, price):
    result = {}
    acoes = code.endswith("F") or code.endswith("3") and not code.endswith("11")

    if code not in assets.keys():
        assets[code] = {
            "qtd": 0,
            "total": 0,
        }

    consolidado = assets[code]

    assets[code]["qtd"] = consolidado["qtd"] + qtd
    assets[code]["total"] += price * qtd

    return {"acum_qtd": assets[code]["qtd"], "acum_val": assets[code]["total"]}


def vende(assets, code, year_month, qtd, price):
    qtd = int(qtd)
    result = {}
    acoes = code.endswith("F") or code.endswith("3") and not code.endswith("11")

    consolidado = assets[code]

    if code not in assets.keys():
        assets[code] = {
            "qtd": 0,
            "total": 0,
        }

    venda_valor = qtd * price
    assets[code]["qtd"] = consolidado["qtd"] - qtd

    if assets[code]["qtd"] == 0:
        compra_valor = assets[code]["total"]
        assets[code]["total"] = 0
    else:
        compra_valor_medio = consolidado["total"] / consolidado["qtd"]
        compra_valor = compra_valor_medio * qtd
        assets[code]["total"] = assets[code]["total"] - compra_valor

    resultado = venda_valor - compra_valor

    result = {
        "acum_qtd": assets[code]["qtd"],
        "acum_val": assets[code]["total"],
    }
    if resultado > 0:
        # lucro
        if not acoes:
            result["lucro"] = resultado
    else:
        # prejuizo
        result["prejuizo"] = resultado
    return result


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
    assets = {}

    items = {}

    for filename in sorted(os.listdir(folder_path)):
        print(filename)
        if filename.startswith("nego"):
            file_path = os.path.join(folder_path, filename)
            rows = get_df_data(file_path)

            for row in rows:
                if row.código_de_negociação == "nan":
                    break
                dt = get_dt(row)
                items[dt] = items.get(dt) or []

                data = {}
                data["dt"] = dt
                data["op"] = row.tipo_de_movimentação
                data["ativo"] = row.código_de_negociação
                data["corretora"] = row.instituição
                data["qtd"] = row.quantidade
                data["price"] = row.preço
                data["total"] = row.valor
                items[dt].insert(0, data)

    with open("planilhas/_nego_controle.csv", "w") as csvfile:
        fieldnames = [
            "dt",
            "op",
            "ativo",
            "corretora",
            "qtd",
            "price",
            "lucro",
            "prejuizo",
            "total",
            "acum_qtd",
            "acum_val",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dt in sorted(items.keys()):
            rows = items[dt]
            for row in rows:
                if row["ativo"].endswith("F") and row["ativo"][-2] in ["3", "1"]:
                    row["ativo"] = row["ativo"][:-1]
                if row["op"] == "Compra":
                    r = compra(assets, row["ativo"], dt[:-3], row["qtd"], row["price"])
                else:
                    r = vende(assets, row["ativo"], dt[:-3], row["qtd"], row["price"])

                row.update(r)
                writer.writerow(row)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
