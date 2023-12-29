import graphene

from django_mall_checkout.graphql.storefront.checkout import (
    CheckoutMutation,
    CheckoutQuery,
)
from django_mall_checkout.graphql.storefront.checkout_address import (
    CheckoutAddressQuery,
)
from django_mall_checkout.graphql.storefront.checkout_event import (
    CheckoutEventMutation,
    CheckoutEventQuery,
)
from django_mall_checkout.graphql.storefront.checkout_payment import (
    CheckoutPaymentQuery,
)
from django_mall_checkout.graphql.storefront.checkout_shipment import (
    CheckoutShipmentQuery,
)


class Mutation(
    CheckoutMutation,
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
