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
        reader = csv.DictReader(csvfile, fieldnames=["asset_id", "tp", "imposto"])
        for row in reader:
            d[get_std_name(row["asset_id"])] = row
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
    if number:
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


def compra(events, current_status, isentos, lucro, prejuizo, item):

    h = _report_compra_(item)
    std_name = item["std_name"]

    current_status.setdefault(
        std_name,
        {"isento": 0, "lucro": 0, "prejuizo": 0,
         "acum_qtd": 0, "acum_total": 0, "hist": ""}
    )
    item_status = current_status[std_name]
    item_status['asset_type'] = item["asset_type"]
    item_status["acum_qtd"] += item["qtd"]
    item_status["acum_total"] += item["total"]
    item_status["acum_total"] = round(item_status["acum_total"], 2)
    item_status["hist"] += h

    item_status["preco_medio"] = round(
        item_status["acum_total"] / item_status["acum_qtd"], 2
    )

    item_status["conclusao"] = _format_conclusion_(item_status)

    grp_name = item["group"]
    events.setdefault(grp_name, {})
    events[grp_name].setdefault(item["month"], [])
    event = item.copy()

    event["acum_qtd"] = item_status["acum_qtd"]
    event["acum_total"] = item_status["acum_total"]
    event["preco_medio"] = item_status["preco_medio"]
    events[grp_name][event["month"]].append(event)


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


def vende(events, item_status, isentos, lucro, prejuizo, item):
    grp_name = item["group"]

    events.setdefault(grp_name, {})
    events[grp_name].setdefault(item["month"], [])
    event = item.copy()

    std_name = item["std_name"]
    item_status["hist"] += _report_venda_(item)

    resultado = (item["price"] - item_status["preco_medio"]) * item["qtd"]

    if resultado > 0:
        if item["imposto"] == "isento-ate-20mil":
            isentos.setdefault(grp_name, {})
            isentos[grp_name].setdefault(item["month"], {})
            isentos[grp_name][item["month"]].setdefault(std_name, 0)
            isentos[grp_name][item["month"]][std_name] += resultado
            event["isento"] = resultado
            item_status["isento"] = resultado
        else:
            lucro.setdefault(grp_name, {})
            lucro[grp_name].setdefault(item["month"], {})
            lucro[grp_name][item["month"]].setdefault(std_name, 0)
            lucro[grp_name][item["month"]][std_name] += resultado
            event["lucro"] = resultado
            item_status["lucro"] = resultado

    else:
        prejuizo.setdefault(grp_name, {})
        prejuizo[grp_name].setdefault(item["month"], {})
        prejuizo[grp_name][item["month"]].setdefault(std_name, 0)
        prejuizo[grp_name][item["month"]][std_name] += resultado
        event["prejuizo"] = resultado
        item_status["prejuizo"] = resultado

    item_status["acum_qtd"] -= item["qtd"]
    item_status["acum_total"] = item_status["acum_qtd"] * item_status["preco_medio"]
    if item_status["acum_qtd"]:
        item_status["conclusao"] = _format_conclusion_(item_status)
    else:
        item_status["conclusao"] = f"Total de 0 unidades."

    event["acum_qtd"] = item_status["acum_qtd"]
    event["acum_total"] = item_status["acum_total"]
    event["preco_medio"] = item_status["preco_medio"]
    events[grp_name][event["month"]].append(event)


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
            data["asset_type"] = asset_types[data["std_name"]]["tp"]
            data["imposto"] = asset_types[data["std_name"]]["imposto"]
            data["group"] = (
                data["asset_type"] if data["asset_type"] in ("na", "fii") else "rv"
            )

            yield data


def classify_items(items):
    groups = {}

    for item in items:
        group_name = item["group"]
        item_dt = item["dt"]
        groups.setdefault(group_name, {})
        groups[group_name].setdefault(item_dt, [])
        groups[group_name][item_dt].append(item)

    return groups


def report_events(events, groups, assets, isentos, lucros, prejuizos):
    for grp_name, grp_dates in groups.items():
        for dt in sorted(grp_dates.keys()):
            for item in grp_dates[dt]:
                if item["op"] == "Compra":
                    compra(events, assets, isentos, lucros, prejuizos, item)
                else:
                    vende(
                        events,
                        assets[item["std_name"]],
                        isentos,
                        lucros,
                        prejuizos,
                        item,
                    )


def desconta_prejuizo(lucros, prejuizos):
    items = []
    prej_acum = {"rv": 0, "fii": 0}
    for grp_name in ("rv", "fii"):
        months = set(lucros[grp_name].keys()) | set(prejuizos[grp_name].keys())
        for month in sorted(months):
            print(month)
            prejuizo_inicial = prej_acum[grp_name]
            try:
                print(lucros[grp_name][month].values())
                lucro_no_mes = sum(lucros[grp_name][month].values())
            except KeyError as e:
                print(e)
                lucro_no_mes = 0
            try:
                print(prejuizos[grp_name][month].values())
                prejuizo_no_mes = sum(prejuizos[grp_name][month].values())
            except KeyError as e:
                print(e)
                prejuizo_no_mes = 0

            # Acumula o prejuizo
            prej_acum[grp_name] += prejuizo_no_mes

            print(f"prejuizo_inicial = {prejuizo_inicial}")
            print(f"lucro_no_mes mes= {lucro_no_mes}")
            print(f"prejuizo_no_mes = {prejuizo_no_mes}")

            if lucro_no_mes <= 0:
                continue

            # Calcula o lucro, deduzindo o prejuizo
            for ativo, lucro in lucros[grp_name][month].items():
                # lucros[grp_name][month][ativo]
                diff = lucro + prej_acum[grp_name]

                if diff > 0:
                    lucros[grp_name][month][ativo] += prej_acum[grp_name]
                    prej_acum[grp_name] = 0
                else:
                    prej_acum[grp_name] += lucro
                    lucros[grp_name][month][ativo] = 0

            lucro_final_no_mes = sum(lucros[grp_name][month].values())
            yield {
                "grp_name": grp_name,
                "mes": month,
                "ativo": ativo,
                "lucro no mês": lucro_no_mes,
                "prejuizo acumulado inicial": prejuizo_inicial,
                "prejuizo no mês": prejuizo_no_mes,
                "lucro final": lucro_final_no_mes,
                "prejuizo acumulado final": prej_acum[grp_name],
                "imposto15": round(lucro_final_no_mes * 0.15, 2),
                "imposto20": round(lucro_final_no_mes * 0.2, 2),
            }


def salva_lucros_e_prejuizos(isentos, lucros, prejuizos):
    with open("planilhas/impostos/lucros_x_prejuizos.json", "w") as fp:
        fp.write(json.dumps(dict(isentos=isentos, lucros=lucros, prejuizos=prejuizos)))

    with open("planilhas/impostos/lucros_x_prejuizos.csv", "w") as csvfile:
        fieldnames = [
            "grp_name",
            "mes",
            "ativo",
            "lucro no mês",
            "prejuizo acumulado inicial",
            "prejuizo no mês",
            "lucro final",
            "prejuizo acumulado final",
            "imposto15",
            "imposto20",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in desconta_prejuizo(lucros, prejuizos):
            item["lucro no mês"] = _number_to_str(item["lucro no mês"])
            item["prejuizo acumulado inicial"] = _number_to_str(item["prejuizo acumulado inicial"])
            item["prejuizo no mês"] = _number_to_str(item["prejuizo no mês"])
            item["lucro final"] = _number_to_str(item["lucro final"])
            item["prejuizo acumulado final"] = _number_to_str(item["prejuizo acumulado final"])
            item["imposto15"] = _number_to_str(item["imposto15"])
            item["imposto20"] = _number_to_str(item["imposto20"])
            writer.writerow(item)


def salva_status(status):
    fieldnames = [
        "std_name",
        "asset_type",
        "acum_qtd",
        "acum_total",
        "preco_medio",
        "isento",
        "lucro",
        "prejuizo",
        "hist",
    ]

    with open(f"planilhas/impostos/status-2022.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for std_name in sorted(status.keys()):
            status[std_name]["std_name"] = std_name
            status[std_name]["hist"] += status[std_name].pop("conclusao")
            status[std_name]['preco_medio'] = _number_to_str(status[std_name]['preco_medio'])
            status[std_name]['acum_total'] = _number_to_str(status[std_name]['acum_total'])
            status[std_name]["isento"] = _number_to_str(status[std_name]["isento"])
            status[std_name]["lucro"] = _number_to_str(status[std_name]["lucro"])
            status[std_name]["prejuizo"] = _number_to_str(status[std_name]["prejuizo"])
            writer.writerow(status[std_name])


def salva_events(events):
    fieldnames = [
        "month",
        "std_name",
        "op",
        "qtd",
        "price",
        "total",
        "acum_qtd",
        "acum_total",
        "preco_medio",
        "isento",
        "lucro",
        "prejuizo",
    ]
    for grp_name, grp_events in events.items():
        with open(f"planilhas/impostos/events_{grp_name}.csv", "w") as csvfile:

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for month in sorted(grp_events.keys()):
                for item in grp_events[month]:
                    data = {k: item.get(k) for k in fieldnames}
                    data["isento"] = _number_to_str(data["isento"])
                    data["lucro"] = _number_to_str(data["lucro"])
                    data["prejuizo"] = _number_to_str(data["prejuizo"])
                    writer.writerow(data)


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
    events = {}
    isentos = {}

    groups = classify_items(read_files(folder_path))
    report_events(events, groups, assets, isentos, lucros, prejuizos)
    salva_lucros_e_prejuizos(isentos, lucros, prejuizos)
    salva_status(assets)
    salva_events(events)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
