from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    approved_limit = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "monthly_income",
            "approved_limit",
            "age",
        ]

    def validate_monthly_income(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly income must be positive.")
        return value


class LoanSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer = CustomerSerializer(read_only=True)  # nested read-only customer data

    class Meta:
        model = Loan
        fields = [
            "id",
            "customer",
            "loan_amount",
            "tenure",
            "interest_rate",
            "monthly_installment",
            "start_date",
            "end_date",
        ]

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be positive.")
        return value

    def validate_interest_rate(self, value):
        if not (0 < value <= 100):
            raise serializers.ValidationError("Interest rate must be between 0 and 100.")
        return value

    def validate_tenure(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be positive (in months).")
        return value
