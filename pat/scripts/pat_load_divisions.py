import csv
import logging

from django.contrib.auth import get_user_model

from pat.models import Division, Frame, Asset, Broker, Purpose
from pat.scripts.utils import convert_to_float, get_asset_name_and_code


User = get_user_model()


def run(file_path):
    # i ativo   percent size    purpose category    location    scope   portfolio
    fieldnames = [
        "i",
        "ativo",
        "percent",
        "size",
        "purpose",
        "category",
        "location",
        "scope",
        "portfolio",
        "fee",
        "br_fee",
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
            if list(row.keys()) == list(row.values()):
                continue
            # logging.info(row)
            asset = get_asset_name_and_code(row["ativo"])
            asset = Asset.get_or_create(
                name=asset["asset_name"],
                code=asset["asset_code"],
                asset_class=row["category"],
                location=row["location"],
                scope=row["scope"],
                fee=convert_to_float(row["fee"]),
                br_fee=convert_to_float(row["br_fee"]),
                creator=creator,
            )
            if not asset.asset_class:
                logging.error(row)
            Division.get_or_create(
                frame=Frame.get_or_create(row["portfolio"], 1, creator),
                asset=asset,
                size=convert_to_float(row["size"]),
                purpose=Purpose.get_or_create(row["purpose"], creator),
                creator=creator,
            )
