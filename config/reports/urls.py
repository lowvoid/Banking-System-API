from django.urls import path
from .views import TransactionReportView,TransactionExportView,AccountSummaryView,AdminDashboardView

app_name = "reports"

urlpatterns = [
    path("reports/transactions/",TransactionReportView.as_view(),name="transaction_report"),
    path("reports/transactions/export/",TransactionExportView.as_view(),name="transaction_export"),
    path("reports/account-summary/",AccountSummaryView.as_view(),name="account_summary"),
    path("reports/admin/dashboard/",AdminDashboardView.as_view(),name="admin_dashboard")
]
