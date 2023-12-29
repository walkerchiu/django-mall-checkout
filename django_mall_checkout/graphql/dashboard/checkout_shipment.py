import graphene

from django_mall_checkout.graphql.dashboard.types.checkout_shipment import (
    CheckoutShipmentNode,
)


class CheckoutShipmentMutation(graphene.ObjectType):
    pass


class CheckoutShipmentQuery(graphene.ObjectType):
    checkout_shipment = graphene.relay.Node.Field(CheckoutShipmentNode)
