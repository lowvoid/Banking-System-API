from django.contrib import admin
from .models import BankAccount, Transaction


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "account_number", "balance","is_active", "created_at"]
    readonly_fields = ["account_number"]
    list_filter = ["is_active"]
    search_fields = ["account_number", "user__username"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_number", "transaction_type", "account", "amount", "created_at"]
    readonly_fields = ["transaction_number"]
    list_filter = ["transaction_type"]
    search_fields = ["transaction_number", "account__account_number"]
