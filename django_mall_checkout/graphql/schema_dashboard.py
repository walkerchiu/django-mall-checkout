import graphene

from django_mall_checkout.graphql.dashboard.checkout import CheckoutQuery
from django_mall_checkout.graphql.dashboard.checkout_address import CheckoutAddressQuery
from django_mall_checkout.graphql.dashboard.checkout_event import (
    CheckoutEventMutation,
    CheckoutEventQuery,
)
from django_mall_checkout.graphql.dashboard.checkout_payment import CheckoutPaymentQuery
from django_mall_checkout.graphql.dashboard.checkout_shipment import (
    CheckoutShipmentQuery,
)


class Mutation(
    CheckoutEventMutation,
    graphene.ObjectType,
):
    pass


class Query(
    CheckoutQuery,
    CheckoutAddressQuery,
    CheckoutEventQuery,
    CheckoutPaymentQuery,
    CheckoutShipmentQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
