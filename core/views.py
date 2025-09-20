from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import datetime


@api_view(["POST"])
def register_customer(request):
    """
    Register a new customer.
    Approved limit = 36 × monthly_income (rounded to nearest lakh).
    """
    required_fields = ["first_name", "last_name", "phone_number", "monthly_income", "age"]

    for field in required_fields:
        if field not in request.data:
            return Response(
                {"error": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST
            )

    try:
        monthly_income = float(request.data["monthly_income"])
        age = int(request.data["age"])
    except ValueError:
        return Response(
            {"error": "monthly_income must be a number and age must be an integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Round approved limit to nearest lakh (100,000)
    approved_limit = int(round(36 * monthly_income / 100000.0)) * 100000

    customer = Customer.objects.create(
        first_name=request.data["first_name"],
        last_name=request.data["last_name"],
        phone_number=request.data["phone_number"],
        monthly_income=monthly_income,
        approved_limit=approved_limit,
        age=age,
    )

    serializer = CustomerSerializer(customer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check_eligibility(request):
    """
    Check loan eligibility based on customer's credit score and loan parameters.
    """
    try:
        customer_id = request.data["customer_id"]
        loan_amount = float(request.data["loan_amount"])
        interest_rate = float(request.data["interest_rate"])
        tenure = int(request.data["tenure"])
    except (KeyError, ValueError):
        return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)
    credit_score = 100

    on_time_count = sum(1 for l in loans if getattr(l, "emi_paid_on_time", True))
    credit_score -= (len(loans) - on_time_count) * 10

    if len(loans) > 5:
        credit_score -= 10

    current_year = datetime.now().year
    loans_this_year = [l for l in loans if l.start_date.year == current_year]
    if len(loans_this_year) > 2:
        credit_score -= 15

    total_loan_volume = sum(l.loan_amount for l in loans)
    if total_loan_volume > 3 * customer.approved_limit:
        credit_score -= 10

    if getattr(customer, "current_debt", 0) > customer.approved_limit:
        credit_score = 0

    monthly_interest_rate = interest_rate / 100 / 12
    emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure / (
        (1 + monthly_interest_rate) ** tenure - 1
    )

    if emi > 0.5 * customer.monthly_income:
        return Response(
            {
                "customer_id": customer_id,
                "approval": False,
                "reason": "EMI too high compared to income",
            }
        )

    approval = False
    corrected_interest_rate = interest_rate

    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        approval = True
        if interest_rate < 12:
            corrected_interest_rate = 12
    elif 10 < credit_score <= 30:
        approval = True
        if interest_rate < 16:
            corrected_interest_rate = 16

    return Response(
        {
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(emi, 2),
        }
    )


@api_view(["POST"])
def apply_loan(request):
    """
    Process loan application and approve/reject based on eligibility.
    """
    try:
        customer_id = request.data["customer_id"]
        loan_amount = float(request.data["loan_amount"])
        interest_rate = float(request.data["interest_rate"])
        tenure = int(request.data["tenure"])
    except (KeyError, ValueError):
        return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    monthly_interest_rate = interest_rate / 100 / 12
    emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure / (
        (1 + monthly_interest_rate) ** tenure - 1
    )

    loans = Loan.objects.filter(customer=customer)
    credit_score = 100
    on_time_count = sum(1 for l in loans if getattr(l, "emi_paid_on_time", True))
    credit_score -= (len(loans) - on_time_count) * 10

    if len(loans) > 5:
        credit_score -= 10

    current_year = datetime.now().year
    loans_this_year = [l for l in loans if l.start_date.year == current_year]
    if len(loans_this_year) > 2:
        credit_score -= 15

    total_loan_volume = sum(l.loan_amount for l in loans)
    if total_loan_volume > 3 * customer.approved_limit:
        credit_score -= 10

    if getattr(customer, "current_debt", 0) > customer.approved_limit:
        credit_score = 0

    if emi > 0.5 * customer.monthly_income:
        return Response(
            {
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "EMI too high compared to income",
                "monthly_installment": round(emi, 2),
            }
        )

    approved = False
    message = "Loan not approved"

    if credit_score > 50:
        approved = True
        message = "Loan approved"
    elif 30 < credit_score <= 50 and interest_rate >= 12:
        approved = True
        message = "Loan approved with adjusted interest rate"
    elif 10 < credit_score <= 30 and interest_rate >= 16:
        approved = True
        message = "Loan approved with adjusted interest rate"

    if approved:
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=interest_rate,
            monthly_installment=emi,
            status="APPROVED",
        )
        loan_id = loan.id
    else:
        loan_id = None

    return Response(
        {
            "loan_id": loan_id,
            "customer_id": customer_id,
            "loan_approved": approved,
            "message": message,
            "monthly_installment": round(emi, 2),
        }
    )


@api_view(["GET"])
def view_loan(request, loan_id):
    """
    Retrieve details of a specific loan by ID.
    """
    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LoanSerializer(loan)
    return Response(serializer.data)


@api_view(["GET"])
def view_loans(request, customer_id):
    """
    Retrieve all loans associated with a specific customer ID.
    """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)
    serializer = LoanSerializer(loans, many=True)
    return Response(serializer.data)
