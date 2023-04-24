import logging

from django.contrib.auth import get_user_model
from dateutil.parser import parse

from pat.models import Portfolio, Frame


User = get_user_model()


def run(position_date):
    creator = User.objects.first()
    position_date = parse(position_date)
    for frame in Frame.objects.iterator():
        logging.info(frame)
        p = Portfolio.get_or_create(
            frame=frame,
            position_date=position_date,
            creator=creator,
        )
