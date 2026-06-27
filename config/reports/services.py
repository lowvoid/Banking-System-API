from datetime import date, datetime
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.utils import timezone
from bankaccount.models import BankAccount, Transaction


class ReportService:
    @staticmethod
    def get_transaction_report(user, **filters):
        qs = Transaction.objects.filter(
            account__user=user
        ).select_related("account")

        if filters.get("account_id"):
            qs = qs.filter(account_id=filters["account_id"])

        if filters.get("transaction_type"):
            qs = qs.filter(transaction_type=filters["transaction_type"])

        if filters.get("date_from"):
            qs = qs.filter(created_at__gte=filters["date_from"])

        if filters.get("date_to"):
            qs = qs.filter(created_at__lte=filters["date_to"])

        if filters.get("min_amount") is not None:
            qs = qs.filter(amount__gte=Decimal(str(filters["min_amount"])))

        if filters.get("max_amount") is not None:
            qs = qs.filter(amount__lte=Decimal(str(filters["max_amount"])))

        return qs.order_by("-created_at")

    @staticmethod
    def get_account_summary(user):
        accounts = BankAccount.objects.filter(user=user)
        summary = []
        for acc in accounts:
            deposits = Transaction.objects.filter(
                account=acc,
                transaction_type=Transaction.TransactionType.DEPOSIT,
            ).aggregate(total=Sum("amount"), count=Count("id"))

            withdrawals = Transaction.objects.filter(
                account=acc,
                transaction_type=Transaction.TransactionType.WITHDRAWAL,
            ).aggregate(total=Sum("amount"), count=Count("id"))

            summary.append({
                "account_id": acc.id,
                "account_number": acc.account_number,
                "current_balance": str(acc.balance),
                "is_active": acc.is_active,
                "created_at": acc.created_at.isoformat(),
                "total_deposits": str(deposits["total"] or Decimal("0.00")),
                "deposit_count": deposits["count"],
                "total_withdrawals": str(withdrawals["total"] or Decimal("0.00")),
                "withdrawal_count": withdrawals["count"],
            })
        return summary

    @staticmethod
    def get_admin_dashboard():
        total_accounts = BankAccount.objects.count()
        active_accounts = BankAccount.objects.filter(is_active=True).count()

        today = timezone.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        tx_today = Transaction.objects.filter(
            created_at__range=(today_start, today_end)
        ).aggregate(
            total=Sum("amount"),
            count=Count("id"),
            deposits=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.DEPOSIT)),
            withdrawals=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.WITHDRAWAL)),
        )

        all_time = Transaction.objects.aggregate(
            total=Sum("amount"),
            count=Count("id"),
            deposits=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.DEPOSIT)),
            withdrawals=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.WITHDRAWAL)),
        )

        return {
            "accounts": {
                "total": total_accounts,
                "active": active_accounts,
                "inactive": total_accounts - active_accounts,
            },
            "transactions_today": {
                "count": tx_today["count"] or 0,
                "total_volume": str(tx_today["total"] or Decimal("0.00")),
                "total_deposits": str(tx_today["deposits"] or Decimal("0.00")),
                "total_withdrawals": str(tx_today["withdrawals"] or Decimal("0.00")),
            },
            "transactions_all_time": {
                "count": all_time["count"] or 0,
                "total_volume": str(all_time["total"] or Decimal("0.00")),
                "total_deposits": str(all_time["deposits"] or Decimal("0.00")),
                "total_withdrawals": str(all_time["withdrawals"] or Decimal("0.00")),
            },
        }

    @staticmethod
    def generate_csv_rows(user, filters=None):
        qs = ReportService.get_transaction_report(
            user,
            **filters
        ) if filters else Transaction.objects.filter(
            account__user=user
        ).select_related("account").order_by("-created_at")

        yield ["Date", "Transaction #", "Type", "Account", "Amount", "Balance After"]

        for tx in qs:
            yield [
                tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                tx.transaction_number,
                tx.get_transaction_type_display(),
                tx.account.account_number,
                str(tx.amount),
                str(tx.account.balance),
            ]
