from django.core.exceptions import ValidationError

from django_filters import CharFilter, FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.filters import CharInFilter
from django_app_core.relay.connection import ExtendedConnection
from django_mall_checkout.models import Checkout, CheckoutEvent


class CheckoutType(DjangoObjectType):
    class Meta:
        model = Checkout
        fields = ()


class CheckoutFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    status_in = CharInFilter(field_name="status", lookup_expr="in")

    class Meta:
        model = Checkout
        fields = []

    order_by = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
        )
    )


class CheckoutConnection(graphene.relay.Connection):
    class Meta:
        node = CheckoutType


class CheckoutNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = Checkout
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CheckoutFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    status_payment = graphene.Field(graphene.String, required=True)
    status_shipment = graphene.Field(graphene.String, required=True)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            queryset.select_related(
                "customer",
                "customer__profile",
                "checkoutpayment",
                "checkoutpayment__payment",
                "checkoutshipment",
                "checkoutshipment__shipment",
            )
            .prefetch_related("checkoutevent_set", "checkoutaddress_set")
            .filter(customer_id=info.context.user.id)
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            cls._meta.model.objects.select_related(
                "customer",
                "customer__profile",
                "checkoutpayment",
                "checkoutpayment__payment",
                "checkoutshipment",
                "checkoutshipment__shipment",
            )
            .filter(pk=id, customer_id=info.context.user.id)
            .first()
        )

    @staticmethod
    def resolve_status_payment(root: Checkout, info: ResolveInfo):
        event = (
            CheckoutEvent.objects.filter(checkout=root, type="payment")
            .order_by("-created_at")
            .first()
        )

        return event.status

    @staticmethod
    def resolve_status_shipment(root: Checkout, info: ResolveInfo):
        event = (
            CheckoutEvent.objects.filter(checkout=root, type="shipment")
            .order_by("-created_at")
            .first()
        )

        return event.status
