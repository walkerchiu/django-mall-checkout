import graphene

from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_checkout.graphql.storefront.types.checkout_address import (
    CheckoutAddressNode,
)


class CheckoutAddressMutation(graphene.ObjectType):
    pass


class CheckoutAddressQuery(graphene.ObjectType):
    checkout_address = graphene.relay.Node.Field(CheckoutAddressNode)
    checkout_addresses = DjangoFilterConnectionField(
        CheckoutAddressNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
