import sys
import os
import csv
from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse


def load_asset_type(file_path):
    d = {}
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["asset_id", "tp"])
        for row in reader:
            d[get_std_ativo(row["asset_id"])] = row["tp"]
    return d


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


def compra(asset_type, asset_id, acum, lucro, prejuizo, item):
    y = item["dt"][:4]
    m = item["dt"][:-3]

    price_str = str(item["price"]).replace(".", ",")
    total_str = str(item["total"]).replace(".", ",")

    h = f"{item['date']} - {item['corretora']} - compra de {item['qtd']} unidades, R$ {price_str} cada, total R$ {total_str}. "

    acum.setdefault(asset_id, {"acum_qtd": 0, "acum_total": 0, "hist": ""})

    acum[asset_id]["acum_qtd"] += item["qtd"]
    acum[asset_id]["acum_total"] += item["total"]
    acum[asset_id]["acum_total"] = round(acum[asset_id]["acum_total"], 2)
    acum[asset_id]["hist"] += h

    acum[asset_id]["preco_medio"] = round(
        acum[asset_id]["acum_total"] / acum[asset_id]["acum_qtd"], 2
    )

    qtd = acum[asset_id]["acum_qtd"]
    total_str = str(acum[asset_id]["acum_total"]).replace(".", ",")
    preco_medio_str = str(acum[asset_id]["preco_medio"]).replace(".", ",")
    acum[asset_id][
        "conclusao"
    ] = f"Total: {qtd} unidades, R$ {total_str}. Preço médio: R$ {preco_medio_str}. "


def vende(asset_type, asset_id, acum, lucro, prejuizo, item):
    price_str = str(round(item["price"], 2)).replace(".", ",")
    total_str = str(item["total"]).replace(".", ",")
    acum[asset_id][
        "hist"
    ] += f"{item['date']} - {item['corretora']} - venda de {item['qtd']} unidades, R$ {price_str} cada, total R$ {total_str}. "

    resultado = (item["price"] - acum[asset_id]["preco_medio"]) * item["qtd"]

    if resultado > 0:
        lucro.setdefault(asset_id, {})
        m = item["dt"][:-3]
        lucro[asset_id].setdefault(m, 0)
        lucro[asset_id][m] += resultado
    else:
        asset_tp = asset_type[asset_id]
        prejuizo[asset_tp] += resultado

    acum[asset_id]["acum_qtd"] -= item["qtd"]
    acum[asset_id]["acum_total"] = (
        acum[asset_id]["acum_qtd"] * acum[asset_id]["preco_medio"]
    )

    qtd = acum[asset_id]["acum_qtd"]
    preco_medio_str = str(acum[asset_id]["preco_medio"]).replace(".", ",")
    total_str = str(acum[asset_id]["acum_total"]).replace(".", ",")
    if acum[asset_id]["acum_qtd"]:
        acum[asset_id][
            "conclusao"
        ] = f"Total: {qtd} unidades, R$ {total_str}. Preço médio: R$ {preco_medio_str}. "
    else:
        acum[asset_id]["conclusao"] = f"Total de 0 unidades."


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


def get_std_ativo(ativo):
    if ativo.endswith("F") and ativo[-2] in ["3", "1"]:
        return ativo[:-1]
    return ativo


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

    asset_types = load_asset_type("planilhas/asset_type.csv")

    for filename in sorted(os.listdir(folder_path)):
        if filename.startswith("nego") and filename.endswith("12-31.xlsx"):
            print(filename)
            file_path = os.path.join(folder_path, filename)
            rows = get_df_data(file_path)

            for row in rows:
                if row.código_de_negociação == "nan":
                    break
                dt = get_dt(row)
                data = {}
                data["dt"] = dt
                data["date"] = row.data_do_negócio
                data["op"] = row.tipo_de_movimentação
                data["ativo"] = row.código_de_negociação
                data["corretora"] = row.instituição
                data["qtd"] = int(row.quantidade)
                data["price"] = float(row.preço)
                data["total"] = float(row.valor)

                std_ativo = get_std_ativo(row.código_de_negociação)
                assets.setdefault(std_ativo, {})
                assets[std_ativo].setdefault(dt, [])
                assets[std_ativo][dt].append(data)

    acum = {}
    lucros = {}
    prejuizos = {"acao": 0, "fii": 0}
    for asset_id in sorted(assets.keys()):
        for dt in sorted(assets[asset_id].keys()):
            for item in assets[asset_id][dt]:
                if item["op"] == "Compra":
                    compra(asset_types, asset_id, acum, lucros, prejuizos, item)
                else:
                    vende(asset_types, asset_id, acum, lucros, prejuizos, item)

    with open("planilhas/_nego_preco_medio.csv", "w") as csvfile:
        fieldnames = [
            "ativo",
            "acum_qtd",
            "acum_total",
            "preco_medio",
            "hist",
            "conclusao",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for asset_id, result in acum.items():
            result["ativo"] = asset_id
            writer.writerow(result)

    with open("planilhas/_nego_lucro_ou_prej.csv", "w") as csvfile:
        fieldnames = [
            "mes",
            "ativo",
            "lucro",
            "prejuizo",
            "lucro - prejuizo",
            "imposto1",
            "imposto2",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for asset_id in acum.keys():
            try:
                asset_lucro = lucros[asset_id]
            except KeyError:
                continue
            for month in sorted(asset_lucro.keys()):
                prej = prejuizos[asset_types[asset_id]]
                if prej != 0:
                    m_prej = -1 * prej
                    lucro = asset_lucro[month]
                    if lucro >= m_prej:
                        prejuizos[asset_types[asset_id]] += lucro
                        diff = lucro - prej
                    else:
                        prejuizos[asset_types[asset_id]] += lucro
                        diff = 0

                result = {
                    "ativo": asset_id,
                    "mes": month,
                    "lucro": lucro,
                    "prejuizo": prejuizos[asset_types[asset_id]],
                    "lucro - prejuizo": diff,
                    "imposto1": round(diff * 0.15, 2),
                    "imposto2": round(diff * 0.2, 2),
                }
                writer.writerow(result)

        for asset_type, prej in prejuizos.items():
            result = {
                "ativo": asset_id,
                "prejuizo": round(prejuizos[asset_type], 2),
            }
            writer.writerow(result)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
