import sys
import os
import csv
import json
from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse


def load_asset_type(file_path):
    d = {}
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["asset_id", "tp"])
        for row in reader:
            d[get_std_name(row["asset_id"])] = row["tp"]
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


def _number_to_str(number):
    n = round(number, 2)
    s = "{:1.2f}".format(n)
    return s.replace(".", ",")


def _report_compra_(item):
    price_str = _number_to_str(item["price"])
    total_str = _number_to_str(item["total"])
    return " ".join(
        [
            str(item["date"]),
            # item['corretora'],
            f"compra R${total_str} ({item['qtd']} x R${price_str}); ",
        ]
    )


def _format_conclusion_(item_status):
    qtd = item_status["acum_qtd"]
    total_str = _number_to_str(item_status["acum_total"])
    preco_medio_str = _number_to_str(item_status["preco_medio"])
    return f"Preço médio: R${preco_medio_str}, qtd: {qtd}, R${total_str}. "


def compra(current_status, lucro, prejuizo, item):

    h = _report_compra_(item)
    std_name = item["std_name"]

    current_status.setdefault(std_name, {"acum_qtd": 0, "acum_total": 0, "hist": ""})

    current_status[std_name]["acum_qtd"] += item["qtd"]
    current_status[std_name]["acum_total"] += item["total"]
    current_status[std_name]["acum_total"] = round(
        current_status[std_name]["acum_total"], 2
    )
    current_status[std_name]["hist"] += h

    current_status[std_name]["preco_medio"] = round(
        current_status[std_name]["acum_total"] / current_status[std_name]["acum_qtd"], 2
    )

    current_status[std_name]["conclusao"] = _format_conclusion_(
        current_status[std_name]
    )


def _report_venda_(item):
    price_str = _number_to_str(item["price"])
    total_str = _number_to_str(item["total"])
    return " ".join(
        [
            str(item["date"]),
            # item['corretora'],
            f"venda R${total_str} ({item['qtd']} x R${price_str}); ",
        ]
    )


def vende(item_status, lucro, prejuizo, item):
    std_name = item["std_name"]
    item_status["hist"] += _report_venda_(item)

    resultado = (item["price"] - item_status["preco_medio"]) * item["qtd"]

    item_type = item["type"]
    if resultado > 0:
        lucro.setdefault(item_type, {})
        lucro[item_type].setdefault(item["month"], {})
        lucro[item_type][item["month"]].setdefault(std_name, 0)
        lucro[item_type][item["month"]][std_name] += resultado
    else:
        prejuizo[item_type] += resultado

    item_status["acum_qtd"] -= item["qtd"]
    item_status["acum_total"] = item_status["acum_qtd"] * item_status["preco_medio"]
    if item_status["acum_qtd"]:
        item_status["conclusao"] = _format_conclusion_(item_status)
    else:
        item_status["conclusao"] = f"Total de 0 unidades."


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


def get_std_name(ativo):
    if ativo.endswith("F") and ativo[-2] in ["3", "1"]:
        return ativo[:-1]
    return ativo


def read_files(folder_path):
    asset_types = load_asset_type("planilhas/ops/asset_type.csv")
    for filename in sorted(os.listdir(folder_path)):
        if not filename.startswith("nego"):
            continue
        if not filename.endswith("12-31.xlsx"):
            continue

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
            data["year"] = dt[:4]
            data["month"] = dt[:-3]
            data["std_name"] = get_std_name(row.código_de_negociação)
            data["type"] = asset_types[data["std_name"]]
            yield data


def classify_items(items):
    groups = {}

    for item in items:
        asset_type = item["type"]
        item_dt = item["dt"]
        groups.setdefault(asset_type, {})
        groups[asset_type].setdefault(item_dt, [])
        groups[asset_type][item_dt].append(item)

    return groups


def report_events(groups, assets, lucros, prejuizos):
    for grp_type, grp_dates in groups.items():
        prejuizos.setdefault(grp_type, 0)
        lucros.setdefault(grp_type, {})

        for dt in sorted(grp_dates.keys()):
            for item in grp_dates[dt]:
                if item["op"] == "Compra":
                    compra(assets, lucros, prejuizos, item)
                else:
                    vende(assets[item["std_name"]], lucros, prejuizos, item)


def desconta_prejuizo(lucros, prejuizos):
    items = []
    for grp_type, grp_data in lucros.items():
        for month in sorted(grp_data.keys()):
            ativos = grp_data[month]
            for ativo, lucro in ativos.items():
                prej = prejuizos.get(grp_type) or 0
                if lucro >= prej:
                    grp_data[month][ativo] -= prej
                    prejuizos[grp_type] += prej
                else:
                    grp_data[month][ativo] = 0
                    prejuizos[grp_type] -= lucro

                lucro_final = grp_data[month][ativo]
                yield {
                    "grp_type": grp_type,
                    "mes": month,
                    "ativo": ativo,
                    "lucro original": lucro,
                    "prejuizo original": prej,
                    "lucro final": lucro_final,
                    "prejuizo final": prejuizos[grp_type],
                    "imposto1": round(lucro_final * 0.15, 2),
                    "imposto2": round(lucro_final * 0.2, 2),
                }


def salva_lucros_e_prejuizos(lucros, prejuizos):
    with open("planilhas/impostos/lucros_x_prejuizos.json", "w") as fp:
        fp.write(json.dumps({"lucros": lucros, "prejuizos": prejuizos}))

    with open("planilhas/impostos/lucros_x_prejuizos.csv", "w") as csvfile:
        fieldnames = [
            "grp_type",
            "mes",
            "ativo",
            "lucro original",
            "prejuizo original",
            "lucro final",
            "prejuizo final",
            "imposto1",
            "imposto2",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in desconta_prejuizo(lucros, prejuizos):
            writer.writerow(item)


def salva_status(status):

    with open("planilhas/impostos/status.csv", "w") as csvfile:
        fieldnames = [
            "std_name",
            "acum_qtd",
            "acum_total",
            "preco_medio",
            "hist",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for std_name in sorted(status.keys()):
            status[std_name]["std_name"] = std_name
            status[std_name]["hist"] += status[std_name].pop("conclusao")
            writer.writerow(status[std_name])


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
    lucros = {}
    prejuizos = {}

    groups = classify_items(read_files(folder_path))
    report_events(groups, assets, lucros, prejuizos)
    salva_lucros_e_prejuizos(lucros, prejuizos)
    salva_status(assets)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
