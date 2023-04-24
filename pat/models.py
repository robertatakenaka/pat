import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Sum
from django.utils.translation import gettext as _
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.fields import RichTextField

from core.models import CommonControlField


User = get_user_model()


class Broker(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Broker")
        verbose_name_plural = _("Brokers")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class Location(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class Scope(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Scope")
        verbose_name_plural = _("Scopes")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class Purpose(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Purpose")
        verbose_name_plural = _("Purposes")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class IO(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("IO")
        verbose_name_plural = _("IOs")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class Event(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class AssetClass(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Asset Class")
        verbose_name_plural = _("Asset Classses")

        indexes = [
            models.Index(fields=["name"]),
        ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, name=None, creator=None):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.creator = creator
            obj.save()
            return obj


class Asset(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)
    code = models.CharField(_("Code"), max_length=30, null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    br_fee = models.FloatField(null=True, blank=True)
    fee = models.FloatField(null=True, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    scope = models.ForeignKey(Scope, on_delete=models.SET_NULL, null=True, blank=True)
    asset_class = models.ForeignKey(
        AssetClass, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Asset")
        verbose_name_plural = _("Assets")

        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["asset_class"]),
        ]

    def __unicode__(self):
        return f"{self.code or self.name}"

    def __str__(self):
        return f"{self.code or self.name}"

    @classmethod
    def get_or_create(
        cls,
        name=None,
        code=None,
        asset_class=None,
        location=None,
        scope=None,
        fee=None,
        br_fee=None,
        creator=None,
    ):
        items = []
        if code:
            items.append({"code": code})
        if name:
            items.append({"name": name})

        obj = None
        for item in items:
            try:
                obj = cls.objects.get(**item)
                break
            except cls.DoesNotExist:
                pass
        if obj:
            obj.updated_by = creator
            obj.updated = datetime.utcnow()
        else:
            obj = cls()
            obj.creator = creator

        obj.code = obj.code or code
        obj.name = obj.name or name
        obj.asset_class = obj.asset_class or AssetClass.get_or_create(
            asset_class, creator
        )
        obj.location = obj.location or Location.get_or_create(location, creator)
        obj.scope = obj.scope or Scope.get_or_create(scope, creator)
        obj.fee = obj.fee or fee
        obj.br_fee = obj.br_fee or br_fee
        obj.save()
        return obj


class Negotiation(CommonControlField):
    """
    Data do Negócio
    Tipo de Movimentação (compra e venda)
    Mercado
    Prazo/Vencimento
    Instituição
    Código de Negociação
    Quantidade
    Preço
    Valor
    """

    negotiation_date = models.DateField(null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.IntegerField()
    month = models.IntegerField()
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.IntegerField(_("Quantity"), null=True, blank=True)
    price = models.FloatField(_("Price"), null=True, blank=True)
    value = models.FloatField(_("Value"), null=True, blank=True)

    class Meta:
        verbose_name = _("Negociação")
        verbose_name_plural = _("Negociações")

        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["month"]),
            models.Index(fields=["asset"]),
        ]

    @classmethod
    def get_or_create(
        cls,
        negotiation_date=None,
        event=None,
        asset=None,
        broker=None,
        qty=None,
        price=None,
        value=None,
        creator=None,
    ):
        try:
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = None
            return cls.objects.get(
                negotiation_date=negotiation_date,
                broker=broker,
                asset=asset,
                qty=qty,
                price=price,
                event=event,
                value=value,
            )
        except cls.DoesNotExist:
            obj = cls()
            obj.event = event
            obj.negotiation_date = negotiation_date
            obj.year = negotiation_date.year
            obj.month = negotiation_date.month
            obj.broker = broker
            obj.asset = asset
            obj.qty = qty
            obj.price = price
            obj.value = value
            obj.creator = creator
            obj.save()
            return obj


class Movement(CommonControlField):
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

    movement_date = models.DateField(null=True, blank=True)
    io = models.ForeignKey(IO, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.IntegerField()
    month = models.IntegerField()
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.IntegerField(_("Quantity"), null=True, blank=True)
    price = models.FloatField(_("Price"), null=True, blank=True)
    value = models.FloatField(_("Value"), null=True, blank=True)

    class Meta:
        verbose_name = _("Movimentação")
        verbose_name_plural = _("Movimentações")

        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["month"]),
            models.Index(fields=["asset"]),
        ]

    @classmethod
    def get_or_create(
        cls,
        movement_date=None,
        io=None,
        event=None,
        asset=None,
        broker=None,
        qty=None,
        price=None,
        value=None,
        creator=None,
    ):
        try:
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = None
            return cls.objects.get(
                movement_date=movement_date,
                io=io,
                event=event,
                broker=broker,
                asset=asset,
                qty=qty,
                price=price,
                value=value,
            )
        except cls.DoesNotExist:
            obj = cls()
            obj.io = io
            obj.movement_date = movement_date
            obj.event = event
            obj.year = movement_date.year
            obj.month = movement_date.month
            obj.broker = broker
            obj.asset = asset
            obj.qty = qty
            obj.price = price
            obj.value = value
            obj.creator = creator
            obj.save()
            return obj


class Frame(CommonControlField):
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)
    version = models.IntegerField()

    class Meta:
        verbose_name = _("Frame")
        verbose_name_plural = _("Frames")

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["version"]),
        ]

    def __unicode__(self):
        return f"{self.name or ''} {self.version}"

    def __str__(self):
        return f"{self.name or ''} {self.version}"

    @classmethod
    def get_or_create(cls, name=None, version=version, creator=None):
        try:
            return cls.objects.get(name=name, version=version)
        except cls.DoesNotExist:
            obj = cls()
            obj.name = name
            obj.version = version
            obj.creator = creator
            obj.save()
            return obj


class Division(CommonControlField):
    frame = models.ForeignKey(Frame, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    purpose = models.ForeignKey(
        Purpose, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Frame division")
        verbose_name_plural = _("Frame divisions")

        indexes = [
            models.Index(fields=["frame"]),
            models.Index(fields=["asset"]),
        ]

    def __unicode__(self):
        return f"{self.frame or ''} {self.asset or ''}"

    def __str__(self):
        return f"{self.frame or ''} {self.asset or ''}"

    @classmethod
    def get_or_create(
        cls,
        frame=None,
        asset=None,
        size=None,
        purpose=None,
        creator=None,
    ):
        try:
            return cls.objects.get(frame=frame, asset=asset)
        except cls.DoesNotExist:
            obj = cls()
            obj.frame = frame
            obj.asset = asset
            obj.purpose = purpose
            obj.size = size
            obj.creator = creator
            obj.save()
            return obj


class BrokerAssetPosition(CommonControlField):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.FloatField(_("Position"), null=True, blank=True)
    position_date = models.DateField(_("Date"), null=True, blank=True)
    quantity = models.FloatField(_("Quantity"), null=True, blank=True)
    price = models.FloatField(_("Price"), null=True, blank=True)

    class Meta:
        verbose_name = _("BrokerAssetPosition")
        verbose_name_plural = _("BrokerAssetPositions")

        indexes = [
            models.Index(fields=["broker"]),
            models.Index(fields=["asset"]),
            models.Index(fields=["position_date"]),
        ]

    def __unicode__(self):
        return f"{self.position_date or ''} {self.asset} {self.broker}"

    def __str__(self):
        return f"{self.position_date or ''} {self.asset} {self.broker}"

    @classmethod
    def get_or_create(
        cls,
        broker=None,
        asset=None,
        position_date=None,
        position=None,
        quantity=None,
        price=None,
        creator=None,
    ):
        try:
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = None
            return cls.objects.get(
                broker=broker, asset=asset, position_date=position_date
            )
        except cls.DoesNotExist:
            obj = cls()
            obj.broker = broker
            obj.asset = asset
            obj.position_date = position_date
            obj.position = position
            obj.quantity = quantity
            obj.price = price
            obj.creator = creator
            obj.save()
            return obj


class DivisionPosition(CommonControlField):
    division = models.ForeignKey(
        Division, null=True, blank=True, on_delete=models.SET_NULL
    )
    position_date = models.DateField(null=True, blank=True)
    position = models.FloatField(null=True, blank=True)
    diff = models.FloatField(null=True, blank=True)
    percent = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = _("Division Position")
        verbose_name_plural = _("Division Position")

        indexes = [
            models.Index(fields=["division"]),
            models.Index(fields=["position_date"]),
        ]

    def __unicode__(self):
        return f"{self.division} {self.position_date or ''}"

    def __str__(self):
        return f"{self.division} {self.position_date or ''}"

    @classmethod
    def get_or_create(
        cls,
        frame=None,
        asset=None,
        position_date=None,
        creator=None,
    ):
        try:
            div = Division.get_or_create(frame=frame, asset=asset)
            return cls.objects.get(division=div, position_date=position_date)
        except cls.DoesNotExist:
            obj = cls()
            obj.creator = creator
            obj.division = div
            obj.position_date = position_date
            obj.position = 0
            for item in (
                BrokerAssetPosition.objects.filter(
                    position_date=position_date,
                    asset=asset,
                )
                .values("position_date")
                .annotate(total=Sum("position"))
            ):
                obj.position = item["total"]
                break
            obj.diff = obj.position - div.size
            obj.percent = obj.position / div.size if div.size else 1
            obj.save()
            return obj

    # @property
    # def js_label(self):
    #     return self.division.asset.code or self.division.asset.name

    # @property
    # def js_absolute_diff(self):
    #     if self.diff >= 0:
    #         return self.diff
    #     else:
    #         return "{ value: %s, label: labelRight }" % self.diff

    # @property
    # def js_relative_diff(self):
    #     if self.percent >= 0:
    #         return self.percent
    #     else:
    #         return "{ value: %s, label: labelRight }" % self.percent


class Portfolio(CommonControlField):
    position_date = models.DateField(_("Date"), null=True, blank=True)
    frame = models.ForeignKey(Frame, on_delete=models.SET_NULL, null=True, blank=True)
    divisions_positions = models.ManyToManyField(DivisionPosition)

    class Meta:
        verbose_name = _("Portfolio")
        verbose_name_plural = _("Portfolios")

    def __unicode__(self):
        return f"{self.frame or ''} {self.position_date or ''}"

    def __str__(self):
        return f"{self.frame or ''} {self.position_date or ''}"

    @classmethod
    def get_or_create(
        cls,
        position_date,
        frame,
        creator=None,
    ):
        try:
            obj = cls.objects.get(frame=frame, position_date=position_date)
        except cls.DoesNotExist:
            obj = cls()
            obj.creator = creator
            obj.frame = frame
            obj.position_date = position_date
            obj.save()
        for division in Division.objects.filter(frame=frame).iterator():
            division_position = DivisionPosition.get_or_create(
                frame=frame,
                asset=division.asset,
                position_date=position_date,
                creator=creator,
            )
            obj.divisions_positions.add(division_position)
        obj.save()
        return obj

    # @property
    # def js_labels(self):
    #     items = ", ".join(
    #         [item.js_label for item in self.divisions_positions.iterator()]
    #     )
    #     return "[" + items + "]"

    # @property
    # def js_absolute_diff(self):
    #     items = ", ".join(
    #         [str(item.js_absolute_diff) for item in self.divisions_positions.iterator()]
    #     )
    #     return "[{" + items + "}]"

    # @property
    # def js_relative_diff(self):
    #     items = ", ".join(
    #         [str(item.js_relative_diff) for item in self.divisions_positions.iterator()]
    #     )
    #     return "[{" + items + "}]"

    @property
    def assets_position_ordered_by_purpose_and_percent(self):
        for item in self.divisions_positions.filter(division__size__gt=0).order_by(
            "division__purpose__name",
            "percent",
            "diff",
        ):
            yield {
                "purpose": item.division.purpose.name,
                "asset": str(item.division.asset),
                "class": item.division.asset.asset_class.name,
                "position": item.position,
                "expected_position": item.division.size,
                "percent": f"{round(item.percent * 100, 2)}%",
                "diff": item.diff,
            }

    @property
    def subdivision_position_ordered_by_percent(self):
        items = (
            self.divisions_positions.filter(
                division__size__gt=0,
            )
            .values(
                "division__purpose__name",
                "division__asset__asset_class__name",
            )
            .annotate(
                purpose_position=Sum("position"),
                purpose_total=Sum("division__size"),
                purpose_diff=Sum("diff"),
                purpose_percent=(Sum("position") / Sum("division__size")),
            )
            .order_by("purpose_percent")
        )
        return items

    @property
    def division_position_ordered_by_percent(self):
        items = (
            self.divisions_positions.values(
                "division__purpose__name",
            )
            .annotate(
                purpose_position=Sum("position"),
                purpose_total=Sum("division__size"),
                purpose_diff=Sum("diff"),
                purpose_percent=(Sum("position") / Sum("division__size")),
            )
            .order_by("purpose_percent")
        )
        return items

    @property
    def fidel_division_position_ordered_by_percent(self):
        items = (
            self.divisions_positions.filter(
                division__size__gt=0,
            )
            .values(
                "division__purpose__name",
            )
            .annotate(
                purpose_position=Sum("position"),
                purpose_total=Sum("division__size"),
                purpose_diff=Sum("diff"),
                purpose_percent=(Sum("position") / Sum("division__size")),
            )
            .order_by("purpose_percent")
        )
        return items

    @property
    def total(self):
        for item in self.divisions_positions.values("portfolio").annotate(
            total=Sum("position")
        ):
            return item["total"]
