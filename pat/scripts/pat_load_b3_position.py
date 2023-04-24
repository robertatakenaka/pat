import logging
from datetime import date

import pandas as pd
from dateutil.parser import parse
from django.contrib.auth import get_user_model

from pat.models import BrokerAssetPosition, Asset, Broker
from pat.scripts.utils import convert_to_float

User = get_user_model()


def run(file_path, position_date):
    position_date = parse(position_date)
    logging.info(position_date)
    data = pd.read_excel(file_path, sheet_name="Tesouro Direto")
    df = pd.DataFrame(data)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    # df["valor_líquido"] = pd.to_numeric(df["valor_líquido"], errors='coerce')
    # df["quantidade"] = pd.to_numeric(df["quantidade"], errors='coerce')
    creator = User.objects.first()
    for row in df.itertuples(name="Ativo", index=False):

        if "nan" == str(row.produto):
            logging.info("break")
            break

        asset = Asset.get_or_create(name=row.produto, creator=creator)
        broker = Broker.get_or_create(name=row.instituição, creator=creator)
        BrokerAssetPosition.get_or_create(
            broker=broker,
            asset=asset,
            position_date=position_date,
            position=row.valor_líquido,
            quantity=row.quantidade,
            creator=creator,
        )

    logging.info("****************************************")

    for sheet_name in ("Acoes", "BDR", "ETF", "Fundo de Investimento"):
        logging.info("-------------------------------------")
        logging.info(sheet_name)
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        df = pd.DataFrame(data)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("(", "")
            .str.replace(")", "")
        )
        # df["preço_de_fechamento"] = pd.to_numeric(df["preço_de_fechamento"], errors='coerce')
        # df["valor_atualizado"] = pd.to_numeric(df["valor_atualizado"], errors='coerce')
        # df["quantidade"] = pd.to_numeric(df["quantidade"], errors='coerce')

        for row in df.itertuples(name="Ativo", index=False):
            if "nan" == str(row.produto):
                logging.info("break")
                break
            asset = Asset.get_or_create(
                name=row.produto,
                code=row.código_de_negociação,
                creator=creator,
            )
            broker = Broker.get_or_create(name=row.instituição, creator=creator)
            logging.info(asset.asset_class.name)
            BrokerAssetPosition.get_or_create(
                broker=broker,
                asset=asset,
                position_date=position_date,
                position=row.valor_atualizado,
                quantity=row.quantidade,
                price=row.preço_de_fechamento,
                creator=creator,
            )
