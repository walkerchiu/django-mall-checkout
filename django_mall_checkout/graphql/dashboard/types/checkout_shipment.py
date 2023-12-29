from django_filters import FilterSet, OrderingFilter
from django_prices.models import MoneyField
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_app_core.types import Money
from django_mall_checkout.models import CheckoutShipment


class CheckoutShipmentType(DjangoObjectType):
    class Meta:
        model = CheckoutShipment
        fields = ()


@convert_django_field.register(MoneyField)
def convert_money_field_to_string(field, registry=None):
    return graphene.Field(Money)


class CheckoutShipmentFilter(FilterSet):
    class Meta:
        model = CheckoutShipment
        fields = []

    order_by = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
        )
    )


class CheckoutShipmentConnection(graphene.relay.Connection):
    class Meta:
        node = CheckoutShipmentType


class CheckoutShipmentNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = CheckoutShipment
        exclude = (
            "currency",
            "price_amount",
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CheckoutShipmentFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset.select_related("checkout", "shipment")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        return (
            cls._meta.model.objects.select_related("checkout", "shipment")
            .filter(pk=id)
            .first()
        )
