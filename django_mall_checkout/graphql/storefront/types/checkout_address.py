from django.core.exceptions import ValidationError

from django_filters import CharFilter, FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_mall_checkout.models import CheckoutAddress


class CheckoutAddressType(DjangoObjectType):
    class Meta:
        model = CheckoutAddress
        fields = ()


class CheckoutAddressFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")

    class Meta:
        model = CheckoutAddress
        fields = []

    order_by = OrderingFilter(
        fields=(
            "slug",
            "created_at",
            "updated_at",
        )
    )


class CheckoutAddressConnection(graphene.relay.Connection):
    class Meta:
        node = CheckoutAddressType


class CheckoutAddressNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = CheckoutAddress
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CheckoutAddressFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return queryset.select_related("checkout").filter(
            checkout__customer_id=info.context.user.id
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            cls._meta.model.objects.select_related("checkout")
            .filter(pk=id, checkout__customer_id=info.context.user.id)
            .first()
        )
