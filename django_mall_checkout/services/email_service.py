from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import get_template

from django_tenants.utils import schema_context
from graphql_relay import to_global_id

from django_app_account.models import User
from django_app_organization.models import Organization
from django_app_organization.models import ShopPhoto
from django_mall_payment.models import PaymentTrans
from django_mall_product.models import ProductTrans
from django_mall_shipment.models import ShipmentTrans
from django_mall_order.helpers.order_line_item_helper import OrderLineItemHelper


class EmailService:
    def __init__(self):
        name, url, language_code = self._get_shop_data()
        self.shop_name = name
        self.shop_logo = url
        self.shop_language_code = language_code

    def _get_shop_data(self):
        organization = Organization.objects.first()
        shop_translation = organization.translations.filter(
            language_code=organization.language_code
        ).first()

        url = None
        shop_photo = ShopPhoto.objects.filter(
            shop_id=organization.id, slug="organization-logo"
        ).first()
        if shop_photo:
            key = (
                str(organization.id).replace("-", "")
                + "/organization/img-"
                + shop_photo.s3_key
            )
            url = cache.get(key)
            if not url:
                if default_storage.exists(shop_photo.s3_key):
                    url = default_storage.url(shop_photo.s3_key)

                    cache.set(
                        key,
                        url,
                        int(settings.AWS_QUERYSTRING_EXPIRE) - 600,
                    )

        return shop_translation.name, url, organization.language_code

    def send_email(
        self,
        platform: str,
        type: str,
        url: str,
        schema_name: str,
        user: User,
        data: dict = {},
    ) -> bool:
        try:
            match type:
                case "checkout":
                    with schema_context(schema_name):
                        subject = self.shop_name + "-您的訂單已確認"
                        checkout = data["checkout"]
                        order = data["order"]

                        trans = PaymentTrans.objects.get(
                            language_code=self.shop_language_code,
                            payment=checkout.checkoutpayment.payment,
                        )
                        payment_name = trans.name

                        trans = ShipmentTrans.objects.get(
                            language_code=self.shop_language_code,
                            shipment=checkout.checkoutshipment.shipment,
                        )
                        shipment_name = trans.name

                        items = []
                        orderlineitem_set = order.orderlineitem_set.all()
                        for orderlineitem in orderlineitem_set:
                            order_line_item_helper = OrderLineItemHelper(
                                order_line_item=orderlineitem
                            )

                            trans = ProductTrans.objects.get(
                                language_code=self.shop_language_code,
                                product=orderlineitem.variant.product,
                            )

                            items.append(
                                {
                                    "name": trans.name,
                                    "photo_url": order_line_item_helper.get_photo_url(),
                                    "selected_option_values": order_line_item_helper.get_selected_option_values(),
                                    "price_sale_amount": orderlineitem.variant.price_sale_amount,
                                    "quantity": orderlineitem.quantity,
                                    "cost_final_total_amount": orderlineitem.cost_final_total_amount,
                                }
                            )

                        context = {
                            "shop_name": self.shop_name,
                            "shop_logo": self.shop_logo,
                            "user": user,
                            "url": url,
                            "subject": subject,
                            "order_id_global": to_global_id("OrderNode", order.id),
                            "order_serial": order.serial,
                            "payment_name": payment_name,
                            "shipment_name": shipment_name,
                            "items": items,
                            "cost_final_amount": order.cost_final_amount,
                            "cost_shipment_amount": order.cost_shipment_amount,
                            "cost_total_amount": order.cost_total_amount,
                        }
                        template = get_template(
                            platform + "/order_checkout.html"
                        ).render(context)

                        send_mail(
                            subject=subject,
                            message=None,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                            html_message=template,
                        )

                    return True
        except BadHeaderError:
            return False

        return False
