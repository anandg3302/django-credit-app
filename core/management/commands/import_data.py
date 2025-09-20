import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Customer, Loan
from datetime import datetime

class Command(BaseCommand):
    help = "Import customer and loan data from Excel files"

    def handle(self, *args, **kwargs):
        # File paths (adjust if needed)
        customer_file = r"C:\Users\Anand\Downloads\Backend Internship Assignment\customer_data.xlsx"
        loan_file = r"C:\Users\Anand\Downloads\Backend Internship Assignment\loan_data.xlsx"

        # ─── Import Customers ──────────────────────────────────────────────
        self.stdout.write("📥 Importing customers...")
        df_customers = pd.read_excel(customer_file)

        for _, row in df_customers.iterrows():
            Customer.objects.update_or_create(
                phone_number=str(row["Phone Number"]),
                defaults={
                    "first_name": row["First Name"],
                    "last_name": row["Last Name"],
                    "monthly_income": int(row["Monthly Salary"]),
                    "approved_limit": int(row["Approved Limit"]),
                    "age": 30  # You can change this if "Age" exists in Excel
                }
            )
        self.stdout.write("✅ Customers imported successfully.")

        # ─── Import Loans ──────────────────────────────────────────────────
        self.stdout.write("📥 Importing loans...")
        df_loans = pd.read_excel(loan_file)
        print("📋 Loan data columns:", df_loans.columns.tolist())  # For debug

        for _, row in df_loans.iterrows():
            try:
                customer = Customer.objects.get(id=int(row["Customer ID"]))
            except Customer.DoesNotExist:
                self.stdout.write(f"❌ Customer ID {row['Customer ID']} not found. Skipping loan.")
                continue

            start_date = row.get("Date of Approval")
            end_date = row.get("End Date") if not pd.isna(row.get("End Date")) else None

            Loan.objects.update_or_create(
                id=int(row["Loan ID"]),
                defaults={
                    "customer": customer,
                    "loan_amount": float(row["Loan Amount"]),
                    "tenure": int(row["Tenure"]),
                    "interest_rate": float(row["Interest Rate"]),
                    "monthly_installment": float(row["Monthly payment"]),
                    "start_date": pd.to_datetime(start_date).date() if start_date else None,
                    "end_date": pd.to_datetime(end_date).date() if end_date else None,
                    "status": "APPROVED"
                }
            )
        self.stdout.write("✅ Loans imported successfully.")
