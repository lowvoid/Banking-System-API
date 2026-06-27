from rest_framework import serializers
from bankaccount.models import Transaction


class TransactionReportSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=False)
    transaction_type = serializers.ChoiceField(choices=Transaction.TransactionType.choices, required=False)
    date_from = serializers.DateField(required=False, input_formats=["%Y-%m-%d"])
    date_to = serializers.DateField(required=False, input_formats=["%Y-%m-%d"])
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class AccountSummarySerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    account_number = serializers.CharField()
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    total_deposits = serializers.DecimalField(max_digits=12, decimal_places=2)
    deposit_count = serializers.IntegerField()
    total_withdrawals = serializers.DecimalField(max_digits=12, decimal_places=2)
    withdrawal_count = serializers.IntegerField()
