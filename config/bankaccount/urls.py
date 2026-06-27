from django.urls import path
from .views import BankAccountListCreateView, transactions_view

app_name = "bank_account"

urlpatterns = [
    path("bank-accounts/", BankAccountListCreateView.as_view(), name="create_list_bank_account"),
    path("transactions/", transactions_view, name="create_list_transactions_view"),
]
