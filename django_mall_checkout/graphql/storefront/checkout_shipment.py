import graphene

from django_mall_checkout.graphql.storefront.types.checkout_shipment import (
    CheckoutShipmentNode,
)


class CheckoutShipmentMutation(graphene.ObjectType):
    pass


class CheckoutShipmentQuery(graphene.ObjectType):
    checkout_shipment = graphene.relay.Node.Field(CheckoutShipmentNode)
