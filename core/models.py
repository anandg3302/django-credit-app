from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    age = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.FloatField()
    tenure = models.IntegerField()  # in months
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    status = models.CharField(max_length=20, default="PENDING")  # Default value set here
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Loan {self.id} for {self.customer.first_name} {self.customer.last_name}"
