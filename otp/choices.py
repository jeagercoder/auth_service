from django.db import models
from django.utils.translation import gettext_lazy as _


class OtpType(models.TextChoices):
    REGISTER =  'REGISTER', _('Register')


class OtpVia(models.TextChoices):
    EMAIL = 'EMAIL', _('Email')


class OtpStatus(models.TextChoices):
    OPEN = 'OPEN', _('Open')
    VERIFIED = 'VERIFIED', _('Verified')
    EXPIRED = 'EXPIRED', _('Expired')
    BLOCKED = 'BLOCKED', _('Blocked')
