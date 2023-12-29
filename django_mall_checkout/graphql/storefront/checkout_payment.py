import graphene

from django_mall_checkout.graphql.storefront.types.checkout_payment import (
    CheckoutPaymentNode,
)


class CheckoutPaymentMutation(graphene.ObjectType):
    pass


class CheckoutPaymentQuery(graphene.ObjectType):
    checkout_payment = graphene.relay.Node.Field(CheckoutPaymentNode)
