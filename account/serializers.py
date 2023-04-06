from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from service_lib.auth_service.utils.auth import login

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
    OtpVia,
    OtpStatus
)
from .tasks import send_otp_register


class RegisterAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    otp_token = serializers.CharField(read_only=True)

    class Meta:
        model = TempAccount
        exclude = ['uuid', 'created_at']

    def validate_username(self, value):
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError('username already exists.')
        return value

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError('email already exists.')
        return value

    @transaction.atomic
    def create(self, validated_data):

        otp_register_list = [otp for otp in Otp.objects.filter(
            user_email=validated_data.get('email'),
            otp_status=OtpStatus.OPEN,
            otp_type=OtpType.REGISTER
        )]
        for n in range(len(otp_register_list)):
            otp_register_list[n].otp_status = OtpStatus.EXPIRED
        Otp.objects.bulk_update(otp_register_list, ['otp_status'])

        validated_data['password'] = make_password(validated_data.get('password'))
        instance = super().create(validated_data)

        otp = Otp()
        otp.user_uuid = instance.uuid
        otp.user_email = instance.email
        otp.otp_code = ''.join(random.choice(string.digits) for n in range(6))
        otp.otp_type = OtpType.REGISTER
        otp.otp_via = OtpVia.EMAIL
        otp.otp_token = Otp.generate_token()
        otp.expired_at = timezone.now() + settings.OTP_EXPIRED
        otp.save()

        self.otp_token = otp.otp_token

        data = {
            "template_name": "otp register",
            "user_uuid": otp.user_uuid,
            "user_email": otp.user_email,
            "subject": "Otp Register",
            "context": {
                "username": instance.username,
                "otp_code": otp.otp_code
            }
        }

        send_otp_register.delay(data=data)
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['otp_token'] = self.otp_token
        return ret


class RegisterVerifyOtpSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    otp_token = serializers.CharField(max_length=32, min_length=32, write_only=True)

    def create(self, validated_data):
        try:
            otp = Otp.objects.get(
                otp_token=validated_data.get('otp_token'),
                otp_type=OtpType.REGISTER
            )
        except Otp.DoesNotExist:
            raise serializers.ValidationError({'otp_token': ['OTP token invalid.']})

        if otp.otp_status == OtpStatus.BLOCKED:
            raise serializers.ValidationError({'otp_code': ['OTP attempt exceeded limit.']})

        if otp.trial >= 3:
            otp.otp_status = OtpStatus.BLOCKED
            otp.save()
            raise serializers.ValidationError({'otp_code': ['OTP attempt exceeded limit.']})

        otp.trial = F('trial') + 1
        otp.save()

        if otp.otp_status == OtpStatus.EXPIRED:
            raise serializers.ValidationError({'otp_code': ['OTP has expired.']})

        if otp.is_expired:
            otp.otp_status = OtpStatus.EXPIRED
            otp.save()
            raise serializers.ValidationError({'otp_code': ['OTP has expired.']})

        if otp.otp_code != validated_data.get('otp_code'):
            raise serializers.ValidationError({'otp_code': ['OTP code invalid']})

        temp_account = TempAccount.objects.get(uuid=otp.user_uuid)

        with transaction.atomic():
            instance = Account()
            instance.uuid = temp_account.uuid
            instance.first_name = temp_account.first_name
            instance.last_name = temp_account.last_name
            instance.username = temp_account.username
            instance.email = temp_account.email
            instance.password = temp_account.password
            instance.save()

            otp.otp_status = OtpStatus.VERIFIED
            otp.save()

        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    session = serializers.CharField(read_only=True)

    def create(self, validated_data):
        try:
            instance = Account.objects.get(email=validated_data.get('email'))
        except Account.DoesNotExist:
            raise serializers.ValidationError({'email': ['Email not found.']})

        if not instance.check_password(validated_data.get('password')):
            raise serializers.ValidationError({'password': ['Wrong password.']})
        instance.last_login = timezone.now()
        instance.save()
        session = login(uuid=instance.uuid, username=instance.username, email=instance.email)
        self.session = session
        return instance

    def to_representation(self, instance):
        return {'session': self.session}


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        exclude = [
            'date_joined',
            'last_login',
            'password',
            'groups',
            'user_permissions',
            'is_superuser',
            'is_staff'
        ]

