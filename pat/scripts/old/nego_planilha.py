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
    with open("nego_cons.csv", "w") as csvfile:
        fieldnames = ["dt", "op", "ativo", "corretora", "qtd", "preço", "total"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for filename in os.listdir(folder_path):
            print(filename)
            if filename.startswith("nego"):
                file_path = os.path.join(folder_path, filename)
                rows = get_df_data(file_path)

                for row in rows:
                    if row.código_de_negociação == "nan":
                        continue
                    neg_date = parse(row.data_do_negócio)

                    data = {}
                    data["dt"] = neg_date.isoformat()[:10]
                    data["op"] = row.tipo_de_movimentação
                    data["ativo"] = row.código_de_negociação
                    data["corretora"] = row.instituição
                    data["qtd"] = row.quantidade
                    data["preço"] = row.preço
                    data["total"] = row.valor
                    writer.writerow(data)


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
