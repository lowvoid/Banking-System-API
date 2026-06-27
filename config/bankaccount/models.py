from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .utils import Helper


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_account")
    account_number = models.CharField(max_length=15, unique=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "bank_account"
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        constraints = [models.CheckConstraint(condition=models.Q(balance__gte=0), name="check_account_balance_gte")]
        indexes = [models.Index(fields=["user"]), models.Index(fields=["account_number"])]

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = Helper.generate_account_number(prefix="EG")
        super().save(*args, **kwargs)


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "DP", "Deposit"
        WITHDRAWAL = "WD", "Withdrawal"

    transaction_number = models.CharField(max_length=12, unique=True, blank=True)
    transaction_type = models.CharField(max_length=2, choices=TransactionType.choices)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.account.account_number}"

    def clean(self):
        if (self.transaction_type == self.TransactionType.WITHDRAWAL and self.account.balance < self.amount):
            raise ValidationError("Insufficient balance for withdrawal")

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.transaction_number:
            self.transaction_number = Helper.generate_transaction_number()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "transaction"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["account"]), models.Index(fields=["transaction_type"]), models.Index(fields=["created_at"])]
        