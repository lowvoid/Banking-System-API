from rest_framework import serializers
from .models import BankAccount, Transaction
from .services import ManageBankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BankAccount
        fields = ["id","user","account_number","balance","is_active","created_at"]
        read_only_fields = ["id", "account_number", "balance", "created_at"]

    def create(self, validated_data):
        return ManageBankAccount.create_bank_account(**validated_data)


class BankAccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ["id","account_number","balance","is_active","created_at"]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source="account.account_number", read_only=True)

    class Meta:
        model = Transaction
        fields = ["id","transaction_number","transaction_type","account","account_number","amount","created_at"]
        read_only_fields = ["id","transaction_number","account_number","created_at"]

    def validate_account(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and value.user != request.user:
            raise serializers.ValidationError("Account does not belong to you.")
        if not value.is_active:
            raise serializers.ValidationError("Account is not active.")
        return value

    def validate(self, attrs):
        account = attrs.get("account")
        transaction_type = attrs.get("transaction_type")
        amount = attrs.get("amount", 0)

        if amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})

        if transaction_type == Transaction.TransactionType.WITHDRAWAL and account.balance < amount:
            raise serializers.ValidationError("Insufficient balance for withdrawal.")

        return attrs
