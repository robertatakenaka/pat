from datetime import date
import logging

import pandas as pd
from dateutil.parser import parse
from django.contrib.auth import get_user_model

from pat.models import Negotiation, Asset, Broker, Event
from pat.scripts.utils import convert_to_float


User = get_user_model()


def run(file_path):
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
    creator = User.objects.first()

    for row in df.itertuples(name="Ativo", index=False):
        if row.código_de_negociação == "nan":
            continue
        neg_date = parse(row.data_do_negócio)

        asset = Asset.get_or_create(
            code=row.código_de_negociação,
            creator=creator,
        )
        broker = Broker.get_or_create(name=row.instituição, creator=creator)
        try:
            value = float(row.valor)
        except (ValueError, TypeError):
            value = None
        Negotiation.get_or_create(
            negotiation_date=neg_date,
            event=Event.get_or_create(name=row.tipo_de_movimentação, creator=creator),
            asset=asset,
            broker=broker,
            qty=row.quantidade,
            price=row.preço,
            value=value,
            creator=creator,
        )
