from django.core.exceptions import ValidationError
from django.db import transaction

from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import graphene

from django_app_core.decorators import strip_input
from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_checkout.graphql.dashboard.types.checkout import CheckoutNode
from django_mall_checkout.graphql.dashboard.types.checkout_event import (
    CheckoutEventNode,
)
from django_mall_checkout.models import Checkout, CheckoutEvent
from django_mall_checkout.variables import (
    CHECKOUT_STATUS,
    PAYMENT_STATUS,
    SHIPMENT_STATUS,
)


class CreateCheckoutEvent(graphene.relay.ClientIDMutation):
    class Input:
        checkoutId = graphene.ID(required=True)
        refId = graphene.ID()
        type = graphene.String(description="Accept: payment, shipment. Default: None")
        status = graphene.String(required=True)
        message = graphene.String()

    success = graphene.Boolean()
    checkout = graphene.Field(CheckoutNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        checkoutId = input["checkoutId"]
        refId = input["refId"] if "refId" in input else None
        type = input["type"] if "type" in input else None
        status = input["status"]
        message = input["message"] if "message" in input else None

        if type not in (None, "message", "payment", "shipment"):
            raise ValidationError("Bad Request!")
        elif type is None and status not in CHECKOUT_STATUS:
            raise ValidationError("Bad Request!")
        elif type == "payment" and status not in PAYMENT_STATUS:
            raise ValidationError("Bad Request!")
        elif type == "shipment" and status not in SHIPMENT_STATUS:
            raise ValidationError("Bad Request!")

        try:
            _, checkout_id = from_global_id(checkoutId)
        except:
            raise ValidationError("Bad Request!")

        try:
            checkout = Checkout.objects.get(pk=checkout_id)
        except Checkout.DoesNotExist:
            raise ValidationError("Can not find this checkout!")

        if refId:
            try:
                _, ref_id = from_global_id(refId)
            except:
                raise ValidationError("Bad Request!")

            try:
                ref = CheckoutEvent.objects.get(checkout=checkout, pk=ref_id)
            except CheckoutEvent.DoesNotExist:
                raise ValidationError("Can not find this checkout event!")
        else:
            ref = None

        user = info.context.user

        CheckoutEvent.objects.create(
            checkout=checkout,
            ref=ref,
            user=user,
            type=type,
            status=status,
            message=message,
        )

        if type is None:
            checkout.status = status
            checkout.save()

        return CreateCheckoutEvent(success=True, checkout=checkout)


class CheckoutEventMutation(graphene.ObjectType):
    checkout_event_create = CreateCheckoutEvent.Field()


class CheckoutEventQuery(graphene.ObjectType):
    checkout_event = graphene.relay.Node.Field(CheckoutEventNode)
    checkout_events = DjangoFilterConnectionField(
        CheckoutEventNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
