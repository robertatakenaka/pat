from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse
from django.contrib.auth import get_user_model

from pat.models import Movement, IO, Event, Asset, Broker
from pat.scripts.utils import convert_to_float, get_asset_name_and_code


User = get_user_model()


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
    creator = User.objects.first()
    for row in df.itertuples(name="Ativo", index=False):
        logging.info(row)
        if row.produto == "nan":
            continue
        mov_date = parse(row.data)

        try:
            value = float(row.valor_da_operação)
        except (TypeError, ValueError):
            value = None

        asset_ = get_asset_name_and_code(row.produto)
        asset = Asset.get_or_create(
            name=asset_["asset_name"],
            code=asset_["asset_code"],
            creator=creator,
        )
        broker = Broker.get_or_create(name=row.instituição, creator=creator)
        Movement.get_or_create(
            io=IO.get_or_create(name=row.entrada_saída, creator=creator),
            movement_date=mov_date,
            event=Event.get_or_create(name=row.movimentação, creator=creator),
            asset=asset,
            broker=broker,
            qty=row.quantidade,
            price=row.preço_unitário,
            value=value,
            creator=creator,
        )
