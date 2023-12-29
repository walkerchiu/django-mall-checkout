import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from safedelete.models import HARD_DELETE
import graphene

from django_app_core.decorators import strip_input
from django_app_core.relay.connection import DjangoFilterConnectionField
from django_app_core.types import MailingAddressInput
from django_mall_cart.models import Cart
from django_mall_checkout.graphql.storefront.types.checkout import CheckoutNode
from django_mall_checkout.models import (
    Checkout,
    CheckoutAddress,
    CheckoutEvent,
    CheckoutPayment,
    CheckoutShipment,
)
from django_mall_checkout.helpers.checkout_helper import CheckoutHelper
from django_mall_checkout.helpers.email_helper import EmailHelper
from django_mall_payment.models import Payment
from django_mall_shipment.models import Shipment
from django_mall_order.services.order_service import OrderService


class CancelCheckout(graphene.relay.ClientIDMutation):
    class Input:
        checkoutId = graphene.ID(required=True)

    success = graphene.Boolean()
    checkout = graphene.Field(CheckoutNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        checkoutId = input["checkoutId"]

        try:
            _, checkout_id = from_global_id(checkoutId)
        except:
            raise ValidationError("Bad Request!")

        try:
            checkout = Checkout.objects.get(
                pk=checkout_id, customer_id=info.context.user.id
            )
        except Checkout.DoesNotExist:
            raise ValidationError("Can not find this checkout!")
        else:
            if checkout.status not in ("PENDING"):
                raise ValidationError("The checkout is not available for this action!")

        CheckoutEvent.objects.create(checkout=checkout, type=None, status="CANCELLED")

        checkout.status = "CANCELLED"
        checkout.save()

        return CancelCheckout(success=True, checkout=checkout)


class CreateCheckout(graphene.relay.ClientIDMutation):
    class Input:
        cartId = graphene.ID(required=True)
        paymentId = graphene.ID(required=True)
        shipmentId = graphene.ID(required=True)
        mailingAddressList = graphene.List(
            graphene.NonNull(MailingAddressInput), required=True
        )
        note = graphene.String()

    success = graphene.Boolean()
    checkout = graphene.Field(CheckoutNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(
        cls,
        root,
        info: ResolveInfo,
        **input,
    ):
        cartId = input["cartId"]
        paymentId = input["paymentId"]
        shipmentId = input["shipmentId"]
        mailingAddressList = input["mailingAddressList"]
        note = input["note"]

        try:
            _, cart_id = from_global_id(cartId)
            _, payment_id = from_global_id(paymentId)
            _, shipment_id = from_global_id(shipmentId)
        except:
            raise ValidationError("Bad Request!")

        try:
            payment = Payment.objects.filter(
                Q(published_at__lte=datetime.date.today())
                | Q(published_at__isnull=True),
                is_published=True,
            ).get(id=payment_id)
        except:
            raise ValidationError("Can not find this payment!")

        try:
            shipment = Shipment.objects.filter(
                Q(published_at__lte=datetime.date.today())
                | Q(published_at__isnull=True),
                is_published=True,
            ).get(id=shipment_id)
        except:
            raise ValidationError("Can not find this shipment!")

        try:
            cart = Cart.objects.get(id=cart_id)
        except:
            raise ValidationError("Can not find this cart!")

        checkout_helper = CheckoutHelper()
        result, message = checkout_helper.validate_mailingAddressList(
            mailingAddressList=mailingAddressList
        )
        if not result:
            raise ValidationError(message)

        result, message = checkout_helper.validate_cart(cart=cart)
        if not result:
            raise ValidationError(message)

        checkout = Checkout.objects.create(
            organization=cart.organization,
            customer=cart.customer,
            note=note,
        )

        CheckoutPayment.objects.create(checkout=checkout, payment=payment)
        CheckoutEvent.objects.create(
            checkout=checkout, type="payment", status="PENDING"
        )
        CheckoutShipment.objects.create(
            checkout=checkout,
            shipment=shipment,
            currency=shipment.currency,
            price_amount=shipment.price_amount,
        )
        CheckoutEvent.objects.create(
            checkout=checkout, type="shipment", status="PENDING"
        )

        if payment.slug in ("cash-on-pickup"):
            status = "OK"
        else:
            status = "PENDING"
        CheckoutEvent.objects.create(checkout=checkout, type=None, status=status)
        checkout.status = status
        checkout.save()

        for mailingAddress in mailingAddressList:
            CheckoutAddress.objects.create(
                checkout=checkout,
                slug=mailingAddress["slug"],
                address1=mailingAddress["address1"],
                address2=mailingAddress["address2"],
                city=mailingAddress["city"],
                company=mailingAddress["company"],
                country_code=mailingAddress["country_code"],
                first_name=mailingAddress["first_name"],
                last_name=mailingAddress["last_name"],
                phone=mailingAddress["phone"],
                province=mailingAddress["province"],
                zip=mailingAddress["zip"],
            )

        order_service = OrderService(
            organization=cart.organization, customer=cart.customer
        )
        result, order = order_service.create_order(checkout=checkout, cart=cart)

        if result:
            cart.cartline_set.all().delete(force_policy=HARD_DELETE)

            email_helper = EmailHelper(platform="storefront")
            email_helper.send_email(
                type="checkout",
                user=order.customer,
                data={"checkout": checkout, "order": order},
            )
        else:
            checkout.delete(force_policy=HARD_DELETE)

        return CreateCheckout(success=True, checkout=checkout)


class CheckoutMutation(graphene.ObjectType):
    checkout_cancel = CancelCheckout.Field()
    checkout_create = CreateCheckout.Field()


class CheckoutQuery(graphene.ObjectType):
    checkout = graphene.relay.Node.Field(CheckoutNode)
    checkouts = DjangoFilterConnectionField(
        CheckoutNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
