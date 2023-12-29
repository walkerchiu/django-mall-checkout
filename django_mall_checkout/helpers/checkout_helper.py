from typing import List, Tuple

from django_app_core.types import MailingAddressInput
from django_mall_cart.models import Cart


class CheckoutHelper:
    def validate_mailingAddressList(
        self, mailingAddressList: List[MailingAddressInput]
    ) -> Tuple[bool, str]:
        if mailingAddressList is None or len(mailingAddressList) == 0:
            return False, "The mailingAddressList is invalid!"
        for mailingAddress in mailingAddressList:
            if mailingAddress["slug"] not in ("billing", "shipping"):
                return False, "The slug field in mailingAddress is invalid!"
            if len(mailingAddress["country_code"]) > 6:
                return (
                    False,
                    "The length of the countryCode field in mailingAddress is invalid!",
                )
            if len(mailingAddress["phone"]) > 20:
                return (
                    False,
                    "The length of the phone field in mailingAddress is invalid!",
                )
            if len(mailingAddress["zip"]) > 6:
                return (
                    False,
                    "The length of the zip field in mailingAddress is invalid!",
                )

        return True, None

    def validate_cart(self, cart: Cart) -> Tuple[bool, str]:
        cartline_set = cart.cartline_set.all()

        if cartline_set.count() == 0:
            return False, "The cart should not be empty!"

        for cartline in cartline_set:
            if (
                not cartline.variant.is_visible
                or not cartline.variant.product.is_visible
            ):
                return False, "The cart should be updated!"

        return True, None
