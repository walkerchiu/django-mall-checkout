import threading

from django.db import connection

from django_app_account.models import User
from django_mall_checkout.services.email_service import EmailService

DJANGO_APP_TENANT_INSTALLED = importlib.util.find_spec("django_app_tenant") is not None
if DJANGO_APP_TENANT_INSTALLED:
    from django_app_tenant.utils import get_platform_url


class EmailHelper:
    def __init__(self, platform: str):
        self.service = EmailService()
        self.platform = platform
        self.url = ""
        if DJANGO_APP_TENANT_INSTALLED:
            self.url = get_platform_url(platform=platform)

    def send_email(self, type: str, user: User, data: dict = {}) -> bool:
        match type:
            case "checkout":
                pass

        thread = threading.Thread(
            target=self.service.send_email,
            kwargs={
                "platform": self.platform,
                "type": type,
                "url": self.url,
                "schema_name": connection.schema_name,
                "user": user,
                "data": data,
            },
        )
        thread.start()

        return True
