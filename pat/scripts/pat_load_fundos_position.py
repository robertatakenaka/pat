import csv
import logging

from dateutil.parser import parse
from django.contrib.auth import get_user_model

from pat.models import BrokerAssetPosition, Broker, Asset
from pat.scripts.utils import convert_to_float


User = get_user_model()


def run(file_path, position_date):
    position_date = parse(position_date)
    fieldnames = [
        "broker",
        "fundo",
        "position",
    ]
    creator = User.objects.first()
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            logging.info(row)
            fieldnames = row
            break
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row in reader:
            if list(row.values()) == list(row.keys()):
                continue

            asset = Asset.get_or_create(
                name=row["ATIVO"],
                creator=User.objects.first(),
            )
            broker = Broker.get_or_create(
                name=row["CORRETORA"], creator=User.objects.first()
            )

            BrokerAssetPosition.get_or_create(
                broker=broker,
                asset=asset,
                position_date=position_date,
                position=convert_to_float(row["posição"]),
                creator=creator,
            )
