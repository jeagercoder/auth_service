from django.shortcuts import render

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .models import Account, TempAccount
from .serializers import (
    RegisterAccountSerializer,
    RegisterVerifyOtpSerializer,
    LoginSerializer,
    ProfileSerializer
)


class AccountViewSet(GenericViewSet):
    queryset = Account.objects.filter(is_active=True)
    serializer_class = RegisterAccountSerializer
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterAccountSerializer
        elif self.action == 'register_otp':
            return RegisterVerifyOtpSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'profile':
            return ProfileSerializer
        return super().get_serializer_class()

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def register_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True)
    def profile(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
