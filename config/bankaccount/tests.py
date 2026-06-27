from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BankAccount, Transaction
from .services import ManageBankAccount, ManageTransaction
from .utils import Helper
from reports.services import ReportService


# --- Helper Tests ---

class HelperTests(TestCase):
    def test_generate_account_number_unique(self):
        n1 = Helper.generate_account_number(prefix="EG")
        n2 = Helper.generate_account_number(prefix="EG")
        self.assertNotEqual(n1, n2)
        self.assertTrue(n1.startswith("EG"))
        self.assertEqual(len(n1), 14)

    def test_generate_account_number_with_default_prefix(self):
        n = Helper.generate_account_number()
        self.assertTrue(n.startswith("EG"))
        self.assertEqual(len(n), 14)

    def test_generate_transaction_number_unique(self):
        n1 = Helper.generate_transaction_number()
        n2 = Helper.generate_transaction_number()
        self.assertNotEqual(n1, n2)
        self.assertEqual(len(n1), 12)


# --- Service Tests ---

class ManageBankAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")

    def test_create_bank_account(self):
        account = ManageBankAccount.create_bank_account(user=self.user)
        self.assertIsNotNone(account.account_number)
        self.assertEqual(account.balance, Decimal("0.00"))
        self.assertEqual(account.user, self.user)

    def test_get_user_accounts_filters_by_user(self):
        user2 = User.objects.create_user(username="test2", password="pass123")
        BankAccount.objects.create(user=self.user)
        BankAccount.objects.create(user=user2)
        accounts = ManageBankAccount.get_user_accounts(self.user)
        self.assertEqual(accounts.count(), 1)

    def test_get_account_by_id_returns_none_for_missing(self):
        result = ManageBankAccount.get_account_by_id(999)
        self.assertIsNone(result)


class ManageTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")
        self.account = BankAccount.objects.create(user=self.user, balance=Decimal("1000.00"))

    def test_get_user_transactions_filters_by_user(self):
        user2 = User.objects.create_user(username="test2", password="pass123")
        account2 = BankAccount.objects.create(user=user2)
        Transaction.objects.create(account=self.account, transaction_type="DP", amount=Decimal("100.00"))
        Transaction.objects.create(account=account2, transaction_type="DP", amount=Decimal("100.00"))
        txs = ManageTransaction.get_user_transactions(self.user)
        self.assertEqual(txs.count(), 1)

    def test_get_transaction_by_id_returns_none_for_missing(self):
        result = ManageTransaction.get_transaction_by_id(999)
        self.assertIsNone(result)


# --- Report Service Tests ---

class ReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")
        self.account = BankAccount.objects.create(user=self.user, balance=Decimal("500.00"))
        self.tx1 = Transaction.objects.create(account=self.account, transaction_type="DP", amount=Decimal("200.00"))
        self.tx2 = Transaction.objects.create(account=self.account, transaction_type="WD", amount=Decimal("50.00"))

    def test_get_transaction_report_returns_all(self):
        qs = ReportService.get_transaction_report(self.user)
        self.assertEqual(qs.count(), 2)

    def test_get_transaction_report_filters_by_type(self):
        qs = ReportService.get_transaction_report(self.user, transaction_type="DP")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().transaction_type, "DP")

    def test_get_transaction_report_filters_by_amount_range(self):
        qs = ReportService.get_transaction_report(self.user, min_amount=100, max_amount=300)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().amount, Decimal("200.00"))

    def test_get_account_summary(self):
        summary = ReportService.get_account_summary(self.user)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["account_id"], self.account.id)
        self.assertEqual(Decimal(summary[0]["total_deposits"]), Decimal("200.00"))
        self.assertEqual(Decimal(summary[0]["total_withdrawals"]), Decimal("50.00"))
        self.assertEqual(summary[0]["deposit_count"], 1)
        self.assertEqual(summary[0]["withdrawal_count"], 1)

    def test_get_admin_dashboard(self):
        dash = ReportService.get_admin_dashboard()
        self.assertIn("accounts", dash)
        self.assertIn("transactions_all_time", dash)
        self.assertEqual(dash["accounts"]["total"], 1)
        self.assertEqual(dash["accounts"]["active"], 1)
        self.assertEqual(dash["transactions_all_time"]["count"], 2)

    def test_generate_csv_rows(self):
        rows = list(ReportService.generate_csv_rows(self.user))
        self.assertEqual(len(rows), 3)  # header + 2 transactions
        self.assertEqual(rows[0], ["Date", "Transaction #", "Type", "Account", "Amount", "Balance After"])


# --- API Tests ---

class AuthAPITests(APITestCase):
    def test_register_with_password_mismatch(self):
        response = self.client.post("/api/register/", {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass1!",
            "password2": "DifferentPass1!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post("/api/register/", {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])

    def test_login_with_wrong_password(self):
        User.objects.create_user(username="u", password="correct")
        response = self.client.post("/api/token/", {
            "username": "u",
            "password": "wrong",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BankAccountAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_unauthenticated_request_returns_401(self):
        self.client.credentials()
        response = self.client.get("/api/bank-accounts/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_account(self):
        response = self.client.post("/api/bank-accounts/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("account_number", response.data["data"])

    def test_user_cannot_see_others_accounts(self):
        user2 = User.objects.create_user(username="test2", password="pass123")
        BankAccount.objects.create(user=user2)
        response = self.client.get("/api/bank-accounts/")
        for acc in response.data["data"]:
            self.assertEqual(acc["account_number"], BankAccount.objects.get(user=self.user).account_number)


class TransactionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")
        self.account = BankAccount.objects.create(user=self.user)
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_deposit_increases_balance(self):
        self.client.post("/api/transactions/", {
            "transaction_type": "DP",
            "account": self.account.id,
            "amount": 500.00,
        }, format="json")
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("500.00"))

    def test_withdrawal_decreases_balance(self):
        self.account.balance = Decimal("1000.00")
        self.account.save()
        self.client.post("/api/transactions/", {
            "transaction_type": "WD",
            "account": self.account.id,
            "amount": 300.00,
        }, format="json")
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("700.00"))

    def test_withdrawal_exceeding_balance_returns_400(self):
        self.account.balance = Decimal("100.00")
        self.account.save()
        response = self.client.post("/api/transactions/", {
            "transaction_type": "WD",
            "account": self.account.id,
            "amount": 99999.00,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_transact_on_other_users_account(self):
        user2 = User.objects.create_user(username="test2", password="pass123")
        account2 = BankAccount.objects.create(user=user2)
        response = self.client.post("/api/transactions/", {
            "transaction_type": "DP",
            "account": account2.id,
            "amount": 100.00,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass123")
        self.account = BankAccount.objects.create(user=self.user, balance=Decimal("1000.00"))
        Transaction.objects.create(account=self.account, transaction_type="DP", amount=Decimal("500.00"))
        Transaction.objects.create(account=self.account, transaction_type="WD", amount=Decimal("200.00"))
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_transaction_report_returns_data(self):
        response = self.client.get("/api/reports/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)

    def test_transaction_report_filters(self):
        response = self.client.get("/api/reports/transactions/?transaction_type=DP")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["transaction_type"], "DP")

    def test_transaction_export_returns_csv(self):
        response = self.client.get("/api/reports/transactions/export/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])
        content = response.content.decode("utf-8")
        self.assertIn("Date,Transaction #,Type,Account,Amount,Balance After", content)

    def test_account_summary(self):
        response = self.client.get("/api/reports/account-summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(Decimal(response.data["data"][0]["total_deposits"]), Decimal("500.00"))

    def test_admin_dashboard_requires_admin(self):
        response = self.client.get("/api/reports/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_dashboard_works_for_admin(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/reports/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("accounts", response.data["data"])
        self.assertIn("transactions_today", response.data["data"])
