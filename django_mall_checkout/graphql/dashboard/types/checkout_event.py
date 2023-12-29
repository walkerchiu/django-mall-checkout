from django_filters import BooleanFilter, CharFilter, FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
from graphene_django.filter import GlobalIDFilter
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_mall_checkout.models import CheckoutEvent


class CheckoutEventType(DjangoObjectType):
    class Meta:
        model = CheckoutEvent
        fields = ()


class CheckoutEventFilter(FilterSet):
    ref = GlobalIDFilter(field_name="ref")
    ref_null = BooleanFilter(field_name="ref", lookup_expr="isnull")
    type = CharFilter(field_name="type", lookup_expr="exact")
    type_null = BooleanFilter(field_name="type", lookup_expr="isnull")
    status = CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = CheckoutEvent
        fields = []

    order_by = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
        )
    )


class CheckoutEventConnection(graphene.relay.Connection):
    class Meta:
        node = CheckoutEventType


class CheckoutEventNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = CheckoutEvent
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CheckoutEventFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset.select_related("checkout", "ref", "user", "user__profile")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        return (
            cls._meta.model.objects.select_related(
                "checkout", "ref", "user", "user__profile"
            )
            .filter(pk=id)
            .first()
        )
