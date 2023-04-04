from django.db import models
from django.utils import timezone

import uuid
import string
import random

from .choices import (
    OtpType,
    OtpVia,
    OtpStatus
)
from account.models import Account


class Otp(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_uuid = models.UUIDField(blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)

    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OtpType.choices)
    otp_via = models.CharField(max_length=20, choices=OtpVia.choices, default=OtpVia.EMAIL)
    otp_status = models.CharField(max_length=20, choices=OtpStatus.choices, default=OtpStatus.OPEN)
    otp_token = models.CharField(max_length=32, unique=True)

    trial = models.IntegerField(default=0)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        if self.otp_status != OtpStatus.OPEN:
            return True
        return bool(timezone.now() > self.expired_at)

    @classmethod
    def generate_token(cls):
        token = ''.join(random.choice(string.digits+string.ascii_lowercase) for n in range(32))
        if cls.objects.filter(otp_token=token).exists():
            return cls.generate_token()
        return token
