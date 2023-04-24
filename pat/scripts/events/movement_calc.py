from datetime import date
import logging
import sys

import pandas as pd
from dateutil.parser import parse

# from django.contrib.auth import get_user_model

# from pat.models import Movement, IO, Event, Asset, Broker
# from pat.scripts.utils import convert_to_float, get_asset_name_and_code


def run(file_path):
    """
    Entrada/Saída
    Data
    Movimentação
    Produto
    Instituição
    Quantidade
    Preço unitário
    Valor da Operação
    """
    data = pd.read_excel(file_path, sheet_name="Movimentação")
    df = pd.DataFrame(data)

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("/", "_")
    )
    items = {}
    for row in df.itertuples(name="Ativo", index=False):
        logging.info(row)
        if row.produto == "nan":
            continue
        k = f"{row.produto}\t{row.movimentação}"
        items.setdefault(k, 0)
        try:
            items[k] += float(row.valor_da_operação)
        except:
            pass

    for k in sorted(items.keys()):
        print(f"{k}\t{items[k]}")


if __name__ == "__main__":
    print(sys.argv[1])
    run(sys.argv[1])
