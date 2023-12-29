import graphene

from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_checkout.graphql.dashboard.types.checkout import CheckoutNode


class CheckoutMutation(graphene.ObjectType):
    pass


class CheckoutQuery(graphene.ObjectType):
    checkout = graphene.relay.Node.Field(CheckoutNode)
    checkouts = DjangoFilterConnectionField(
        CheckoutNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
