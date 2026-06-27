import csv
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .services import ReportService
from .serializers import TransactionReportSerializer
from core.utils import api_response


class TransactionReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TransactionReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        transactions = ReportService.get_transaction_report(request.user,**serializer.validated_data)

        data = [
            {
                "id": t.id,
                "transaction_number": t.transaction_number,
                "transaction_type": t.transaction_type,
                "transaction_type_display": t.get_transaction_type_display(),
                "account_id": t.account_id,
                "account_number": t.account.account_number,
                "amount": str(t.amount),
                "created_at": t.created_at.isoformat(),
            }
            for t in transactions
        ]

        return api_response(data=data, message="Transaction report generated successfully", success=True, status=status.HTTP_200_OK)


class TransactionExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TransactionReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        rows = ReportService.generate_csv_rows(request.user,filters=serializer.validated_data)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="transaction_report.csv"'

        writer = csv.writer(response)
        for row in rows:
            writer.writerow(row)

        return response


class AccountSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = ReportService.get_account_summary(request.user)

        return api_response(data=summary,message="Account summary retrieved successfully",success=True,status=status.HTTP_200_OK)


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        dashboard = ReportService.get_admin_dashboard()

        return api_response(data=dashboard,message="Admin dashboard data retrieved successfully",success=True,status=status.HTTP_200_OK)
