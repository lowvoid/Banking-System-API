from django.core.exceptions import ObjectDoesNotExist
from .models import BankAccount, Transaction


class ManageBankAccount:
    @staticmethod
    def get_account_by_id(pk):
        try:
            return BankAccount.objects.get(id=pk)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_user_accounts(user):
        return BankAccount.objects.filter(user=user).select_related("user")

    @staticmethod
    def create_bank_account(**validated_data):
        return BankAccount.objects.create(**validated_data)

    @staticmethod
    def get_all_bank_accounts():
        return BankAccount.objects.select_related("user").all()


class ManageTransaction:
    @staticmethod
    def get_transaction_by_id(pk):
        try:
            return Transaction.objects.get(id=pk)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_user_transactions(user):
        return (Transaction.objects.filter(account__user=user).select_related("account", "account__user").all())

    @staticmethod
    def get_all_transactions():
        return Transaction.objects.select_related("account", "account__user").all()
