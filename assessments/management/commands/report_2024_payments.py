from django.core.management.base import BaseCommand
from assessments.models import Association, UnitAssessment, MonthlyPaymentSchedule
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Generate report of units paid in full as of 12/31/2024'

    def add_arguments(self, parser):
        parser.add_argument('--association', type=str, default='Renaissance Condominium Association',
                          help='Association name')

    def handle(self, *args, **options):
        association_name = options['association']

        # Get the association
        try:
            association = Association.objects.get(name=association_name)
        except Association.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'{association_name} not found'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS(f'2024 PAYMENT REPORT - {association_name}'))
        self.stdout.write(self.style.SUCCESS(f'Report Date: 12/31/2024'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

        # Get all unit assessments for this association
        unit_assessments = UnitAssessment.objects.filter(
            special_assessment__association=association
        ).select_related('unit', 'special_assessment').order_by('unit__unit_number')

        # Categories
        payoff_units = []
        monthly_paid_units = []

        for ua in unit_assessments:
            unit_number = ua.unit.unit_number

            # Check if unit has a payoff
            if ua.payoff_amount and ua.payoff_amount > 0:
                payoff_date = ua.payoff_date
                # Only include payoffs made in or before 2024
                if payoff_date and payoff_date.year <= 2024:
                    payoff_units.append({
                        'unit': unit_number,
                        'amount': ua.payoff_amount,
                        'date': payoff_date,
                        'type': 'Payoff'
                    })

            # Check 2024 monthly payments
            monthly_2024 = MonthlyPaymentSchedule.objects.filter(
                unit_assessment=ua,
                due_date__year=2024
            )

            if monthly_2024.exists():
                total_paid_2024 = sum(s.paid_amount for s in monthly_2024)
                expected_2024 = sum(s.expected_amount for s in monthly_2024)

                # Check if all 2024 payments are made
                if total_paid_2024 >= expected_2024 and total_paid_2024 > 0:
                    monthly_paid_units.append({
                        'unit': unit_number,
                        'amount': total_paid_2024,
                        'type': 'Monthly Payments'
                    })

        # Print Payoff Units Report
        self.stdout.write(self.style.WARNING('\nUNITS PAID OFF IN FULL (Lump Sum):'))
        self.stdout.write('-' * 80)
        self.stdout.write(f'{"Unit":<10} {"Payoff Date":<15} {"Amount Paid":<20}')
        self.stdout.write('-' * 80)

        payoff_total = Decimal('0.00')
        for unit_data in payoff_units:
            self.stdout.write(
                f'{unit_data["unit"]:<10} '
                f'{unit_data["date"].strftime("%m/%d/%Y"):<15} '
                f'${unit_data["amount"]:>18,.2f}'
            )
            payoff_total += unit_data['amount']

        self.stdout.write('-' * 80)
        self.stdout.write(f'{"SUBTOTAL":<10} {"":15} ${payoff_total:>18,.2f}')
        self.stdout.write(f'{"Count: " + str(len(payoff_units)) + " units":<10}\n')

        # Print Monthly Payment Units Report
        self.stdout.write(self.style.WARNING('\nUNITS PAID THROUGH 2024 (Monthly Payments):'))
        self.stdout.write('-' * 80)
        self.stdout.write(f'{"Unit":<10} {"2024 Payments":<20}')
        self.stdout.write('-' * 80)

        monthly_total = Decimal('0.00')
        for unit_data in monthly_paid_units:
            self.stdout.write(
                f'{unit_data["unit"]:<10} '
                f'${unit_data["amount"]:>18,.2f}'
            )
            monthly_total += unit_data['amount']

        self.stdout.write('-' * 80)
        self.stdout.write(f'{"SUBTOTAL":<10} ${monthly_total:>18,.2f}')
        self.stdout.write(f'{"Count: " + str(len(monthly_paid_units)) + " units":<10}\n')

        # Grand Total
        grand_total = payoff_total + monthly_total
        total_units = len(payoff_units) + len(monthly_paid_units)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(self.style.SUCCESS(f'Total Units Paid in Full or Current through 2024: {total_units}'))
        self.stdout.write(self.style.SUCCESS(f'  - Lump Sum Payoffs: {len(payoff_units)} units'))
        self.stdout.write(self.style.SUCCESS(f'  - Monthly Payments Current: {len(monthly_paid_units)} units'))
        self.stdout.write(self.style.SUCCESS(f'\nTotal Amount Collected in 2024: ${grand_total:,.2f}'))
        self.stdout.write(self.style.SUCCESS('=' * 80 + '\n'))
