from django.db import transaction
from django.conf import settings

from rest_framework import serializers

import string
import random
from datetime import datetime

from .models import (
    Account,
    TempAccount
)
from otp.models import Otp
from otp.choices import (
    OtpType,
    OtpVia
)
from .tasks import send_otp_register


class RegisterAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = TempAccount
        exclude = ['uuid', 'created_at', 'account']

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)
        otp = Otp()
        otp.email = instance.email
        otp.otp_code = ''.join(random.choice(string.digits) for n in range(6))
        otp.otp_type = OtpType.REGISTER
        otp.otp_via = OtpVia.EMAIL
        otp.expired_at = datetime.now() + settings.OTP_EXPIRED
        otp.save()

        data = {
            "template_name": "otp register",
            "user_uuid": instance.uuid,
            "user_email": otp.email,
            "subject": "Otp Register",
            "context": {
                "username": instance.username,
                "otp_code": otp.otp_code
            }
        }

        send_otp_register.delay(data=data)
        return instance





