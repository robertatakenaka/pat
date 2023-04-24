from django.contrib.auth import get_user_model

from pat.models import (
    Asset,
    AssetClass,
    BrokerAssetPosition,
    Broker,
    Event,
    IO,
    Location,
    Movement,
    Negotiation,
    Portfolio,
    Purpose,
    Scope,
    Movement,
    Negotiation,
    DivisionPosition,
    Division,
    Frame,
)


User = get_user_model()


def delete(m):
    for item in m.objects.iterator():
        item.delete()
        item.save()


def run():
    delete(AssetClass)

    delete(Broker)

    delete(Frame)

    delete(IO)

    delete(Location)

    delete(Purpose)

    delete(Scope)

    delete(Event)

    delete(Movement)

    delete(Negotiation)

    delete(Asset)

    delete(BrokerAssetPosition)

    delete(Movement)

    delete(Negotiation)

    delete(Division)

    delete(DivisionPosition)

    delete(Portfolio)
