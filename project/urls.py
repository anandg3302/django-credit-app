from django.urls import path
from core.views import (
    register_customer,
    check_eligibility,
    apply_loan,
    view_loan,
    view_loans,
)

urlpatterns = [
    path('register/', register_customer, name='register_customer'),
    path('check-eligibility/', check_eligibility, name='check_eligibility'),
    path('apply-loan/', apply_loan, name='apply_loan'),
    path('view-loan/<int:loan_id>/', view_loan, name='view_loan'),
    path('view-loans/<int:customer_id>/', view_loans, name='view_loans'),
]

