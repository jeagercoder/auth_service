from django.db import models

import uuid
from datetime import datetime

from .choices import (
    OtpType,
    OtpVia
)
from account.models import Account


class Otp(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OtpType.choices)
    otp_via = models.CharField(max_length=20, choices=OtpVia.choices, default=OtpVia.EMAIL)

    trial = models.IntegerField(default=0)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return bool(datetime.now() > self.expired_at)
