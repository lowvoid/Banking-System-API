from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import (BankAccountSerializer,BankAccountDetailSerializer,TransactionSerializer)
from .services import ManageBankAccount, ManageTransaction
from core.utils import api_response


class BankAccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BankAccountDetailSerializer
        return BankAccountSerializer

    def get_queryset(self):
        return ManageBankAccount.get_user_accounts(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(data=BankAccountDetailSerializer(serializer.instance).data,message="Bank account created successfully",success=True,status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data,message="Bank accounts retrieved successfully",success=True,status=status.HTTP_200_OK)


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ManageTransaction.get_user_transactions(self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(data=serializer.data,message="Transaction created successfully",success=True,status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data,message="Transactions retrieved successfully",success=True,status=status.HTTP_200_OK)


transactions_view = TransactionListCreateView.as_view()
