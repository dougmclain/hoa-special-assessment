from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import math


class Association(models.Model):
    """Represents an HOA or Condominium Association"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    management_company = models.CharField(max_length=200, default="Dynamite Management")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SpecialAssessment(models.Model):
    """Represents a special assessment project"""
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='special_assessments')
    name = models.CharField(max_length=200, help_text="e.g., '2024 Special Assessment'")
    description = models.TextField(blank=True)

    # Loan Information
    total_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total loan amount")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Annual interest rate percentage")
    loan_period_months = models.IntegerField(help_text="Number of months for the loan")
    monthly_loan_payment = models.DecimalField(max_digits=12, decimal_places=2, help_text="Association's monthly loan payment")

    # Dates
    start_date = models.DateField(help_text="First payment due date")

    # Total assessment allocation
    total_base_assessment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_lce_assessments = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total Limited Common Element assessments")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.association.name} - {self.name}"

    def monthly_interest_rate(self):
        """Get monthly interest rate as decimal"""
        return (self.interest_rate / 100) / 12

    def calculate_monthly_payment(self, principal):
        """Calculate monthly payment for a given principal using loan amortization formula"""
        if principal == 0:
            return Decimal('0.00')

        r = float(self.monthly_interest_rate())
        n = self.loan_period_months

        if r == 0:
            return Decimal(principal / n).quantize(Decimal('0.01'))

        # M = P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly_payment = float(principal) * (r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        return Decimal(monthly_payment).quantize(Decimal('0.01'))


class Unit(models.Model):
    """Represents a unit/home in the association"""
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=50, help_text="Unit number (e.g., A1, B9, L51)")
    owner_name = models.CharField(max_length=200, blank=True)
    owner_email = models.EmailField(blank=True)
    owner_phone = models.CharField(max_length=20, blank=True)
    common_expense_allocation = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Percentage of common expenses (typically 1% for 100 units)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['unit_number']
        unique_together = ['association', 'unit_number']

    def __str__(self):
        return f"{self.association.name} - Unit {self.unit_number}"


class UnitAssessment(models.Model):
    """Links a unit to a special assessment with specific amounts"""
    PAYMENT_OPTION_LUMP = 'lump'
    PAYMENT_OPTION_MONTHLY = 'monthly'
    PAYMENT_OPTIONS = [
        (PAYMENT_OPTION_LUMP, 'Lump Sum'),
        (PAYMENT_OPTION_MONTHLY, 'Monthly Payments'),
    ]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_assessments')
    special_assessment = models.ForeignKey(SpecialAssessment, on_delete=models.CASCADE, related_name='unit_assessments')

    # Assessment amounts
    base_assessment_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Base assessment amount")

    # Payment option
    payment_option = models.CharField(max_length=10, choices=PAYMENT_OPTIONS, default=PAYMENT_OPTION_MONTHLY)

    # Calculated fields
    monthly_base_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly payment for base assessment with interest")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['unit', 'special_assessment']
        ordering = ['unit__unit_number']

    def __str__(self):
        return f"{self.unit.unit_number} - {self.special_assessment.name}"

    def save(self, *args, **kwargs):
        """Calculate monthly payment on save"""
        if self.payment_option == self.PAYMENT_OPTION_MONTHLY:
            self.monthly_base_payment = self.special_assessment.calculate_monthly_payment(self.base_assessment_amount)
        else:
            self.monthly_base_payment = Decimal('0.00')
        super().save(*args, **kwargs)

    def total_lce_fees(self):
        """Get total of all Limited Common Element fees for this unit assessment"""
        return self.additional_fees.aggregate(total=models.Sum('fee_amount'))['total'] or Decimal('0.00')

    def total_lce_monthly_payment(self):
        """Get total monthly payment for all LCE fees"""
        return self.additional_fees.aggregate(total=models.Sum('monthly_payment'))['total'] or Decimal('0.00')

    def total_assessment_amount(self):
        """Get total assessment (base + all LCE fees)"""
        return self.base_assessment_amount + self.total_lce_fees()

    def total_monthly_payment(self):
        """Get total monthly payment (base + all LCE fees)"""
        if self.payment_option == self.PAYMENT_OPTION_LUMP:
            return Decimal('0.00')
        return self.monthly_base_payment + self.total_lce_monthly_payment()

    def total_paid(self):
        """Get total amount paid so far"""
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def remaining_balance(self):
        """Calculate remaining balance"""
        if self.payment_option == self.PAYMENT_OPTION_LUMP:
            return self.total_assessment_amount() - self.total_paid()
        return self.calculate_payoff_amount()

    def calculate_payoff_amount(self):
        """Calculate the payoff amount at current date"""
        from datetime import date

        if self.payment_option == self.PAYMENT_OPTION_LUMP:
            return self.total_assessment_amount() - self.total_paid()

        # Calculate number of payments made
        total_paid = self.total_paid()
        monthly_payment = self.total_monthly_payment()

        if monthly_payment == 0:
            return Decimal('0.00')

        # This is a simplified calculation - for accurate payoff, we'd need to calculate
        # the remaining principal using amortization schedule
        payments_made = int(total_paid / monthly_payment)
        remaining_months = self.special_assessment.loan_period_months - payments_made

        if remaining_months <= 0:
            return Decimal('0.00')

        # Calculate remaining principal using loan formula
        r = float(self.special_assessment.monthly_interest_rate())
        n = remaining_months
        pmt = float(monthly_payment)

        if r == 0:
            return Decimal(pmt * n).quantize(Decimal('0.01'))

        # Present value of remaining payments
        # PV = PMT * [(1 - (1+r)^-n) / r]
        remaining_principal = pmt * ((1 - math.pow(1 + r, -n)) / r)
        return Decimal(remaining_principal).quantize(Decimal('0.01'))

    def payment_status(self):
        """Get payment status"""
        if self.payment_option == self.PAYMENT_OPTION_LUMP:
            if self.total_paid() >= self.total_assessment_amount():
                return "Paid in Full"
            elif self.total_paid() > 0:
                return "Partial Payment"
            else:
                return "Not Paid"
        else:
            from datetime import date
            from dateutil.relativedelta import relativedelta

            expected_payments = 0
            current_date = date.today()
            payment_date = self.special_assessment.start_date

            while payment_date <= current_date:
                expected_payments += 1
                payment_date = payment_date + relativedelta(months=1)
                if expected_payments >= self.special_assessment.loan_period_months:
                    break

            expected_amount = self.total_monthly_payment() * expected_payments
            paid_amount = self.total_paid()

            if paid_amount >= self.total_assessment_amount():
                return "Paid in Full"
            elif paid_amount >= expected_amount:
                return "Current"
            elif paid_amount > 0:
                return "Behind"
            else:
                return "Not Started"


class AdditionalFee(models.Model):
    """Represents additional fees like Deck, Skylight, etc. (Limited Common Element assessments)"""
    unit_assessment = models.ForeignKey(UnitAssessment, on_delete=models.CASCADE, related_name='additional_fees')
    fee_type = models.CharField(max_length=100, help_text="e.g., 'Deck', 'Skylight', 'Special Item'")
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Additional fee amount")
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly payment for this fee with interest")
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unit_assessment.unit.unit_number} - {self.fee_type}: ${self.fee_amount}"

    def save(self, *args, **kwargs):
        """Calculate monthly payment on save"""
        if self.unit_assessment.payment_option == UnitAssessment.PAYMENT_OPTION_MONTHLY:
            self.monthly_payment = self.unit_assessment.special_assessment.calculate_monthly_payment(self.fee_amount)
        else:
            self.monthly_payment = Decimal('0.00')
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Tracks payments made by units"""
    unit_assessment = models.ForeignKey(UnitAssessment, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=50, blank=True, help_text="e.g., 'Check', 'Wire', 'ACH'")
    reference_number = models.CharField(max_length=100, blank=True, help_text="Check number or transaction reference")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.unit_assessment.unit.unit_number} - ${self.amount} on {self.payment_date}"
