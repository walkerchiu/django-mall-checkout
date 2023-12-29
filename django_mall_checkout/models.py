import uuid

from django.conf import settings
from django.db import models

from django_prices.models import MoneyField
from safedelete.models import SOFT_DELETE_CASCADE

from django_app_account.models import User
from django_app_core.models import CommonDateAndSafeDeleteMixin
from django_app_organization.models import Organization
from django_mall_payment.models import Payment
from django_mall_shipment.models import Shipment


class Checkout(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    customer = models.ForeignKey(User, models.CASCADE)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, db_index=True, blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_checkout_checkout"
        get_latest_by = "updated_at"

    def __str__(self):
        return str(self.id)


class CheckoutEvent(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkout = models.ForeignKey(Checkout, models.CASCADE)
    ref = models.ForeignKey("self", models.CASCADE, null=True)
    user = models.ForeignKey(User, models.CASCADE, null=True)
    type = models.CharField(max_length=10, db_index=True, blank=True, null=True)
    status = models.CharField(max_length=20, db_index=True)
    message = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_checkout_event"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)


class CheckoutPayment(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkout = models.OneToOneField(Checkout, models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.RESTRICT)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_checkout_payment"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)


class CheckoutShipment(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkout = models.OneToOneField(Checkout, models.CASCADE)
    shipment = models.ForeignKey(Shipment, on_delete=models.RESTRICT)
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY_CODE,
    )
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    price = MoneyField(amount_field="price_amount", currency_field="currency")

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_checkout_shipment"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)


class CheckoutAddress(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkout = models.ForeignKey(Checkout, models.CASCADE)
    slug = models.CharField(max_length=255, db_index=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=6, db_index=True, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, db_index=True, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=6, db_index=True, blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_checkout_address"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)
