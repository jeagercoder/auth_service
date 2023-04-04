from django.shortcuts import render

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .models import Account, TempAccount
from .serializers import RegisterAccountSerializer


class AccountViewSet(GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = RegisterAccountSerializer

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterAccountSerializer
        return super().get_serializer_class()

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

