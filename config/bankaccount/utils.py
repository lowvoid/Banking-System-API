from django.apps import apps
import random
import string


class Helper:
    MAX_RETRIES = 100

    @staticmethod
    def generate_account_number(prefix="EG"):
        model = apps.get_model("bankaccount", "BankAccount")
        for _ in range(Helper.MAX_RETRIES):
            unique_part = "".join(random.choices(string.digits, k=12))
            account_number = f"{prefix or ''}{unique_part}"
            if not model.objects.filter(account_number=account_number).exists():
                return account_number
        raise RuntimeError("Could not generate unique account number after maximum retries")

    @staticmethod
    def generate_transaction_number():
        model = apps.get_model("bankaccount", "Transaction")
        for _ in range(Helper.MAX_RETRIES):
            unique_number = "".join(random.choices(string.digits, k=12))
            if not model.objects.filter(transaction_number=unique_number).exists():
                return unique_number
        raise RuntimeError("Could not generate unique transaction number after maximum retries")
