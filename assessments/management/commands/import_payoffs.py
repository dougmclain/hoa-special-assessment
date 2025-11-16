from django.core.management.base import BaseCommand
from assessments.models import Association, Unit, UnitAssessment
from decimal import Decimal
from datetime import datetime


class Command(BaseCommand):
    help = 'Import payoff amounts for Renaissance Condominium Association units'

    def handle(self, *args, **options):
        # Payoff data: (unit_number, payoff_date, payoff_amount)
        payoff_data = [
            ('A3', '08/30/2024', '34,199.68'),
            ('A5', '09/01/2024', '33,225.68'),
            ('A6', '09/01/2024', '33,225.68'),
            ('A7', '08/27/2024', '34,199.68'),
            ('A8', '08/27/2024', '34,199.68'),
            ('C11', '08/27/2024', '33,225.68'),
            ('C13', '09/30/2024', '33,824.11'),
            ('C18', '08/27/2024', '33,712.68'),
            ('E22', '08/27/2024', '33,225.68'),
            ('E23', '08/27/2024', '33,712.68'),
            ('G31', '08/30/2024', '33,225.68'),
            ('G32', '08/27/2024', '33,225.68'),
            ('G37', '08/29/2024', '34,199.68'),
            ('G38', '08/30/2024', '33,712.68'),
            ('H40', '09/01/2024', '34,199.68'),
            ('J41', '09/01/2024', '33,225.68'),
            ('J42', '08/27/2024', '33,225.68'),
            ('J44', '08/23/2024', '34,199.68'),
            ('J46', '08/26/2024', '33,225.68'),
            ('L52', '08/29/2024', '44,751.50'),
            ('L55', '08/27/2024', '33,225.68'),
            ('M59', '09/01/2024', '34,199.68'),
            ('N67', '08/30/2024', '34,199.68'),
            ('N68', '08/30/2024', '33,712.68'),
            ('Q72', '08/30/2024', '33,225.68'),
            ('Q75', '09/01/2024', '33,225.68'),
            ('Q77', '08/29/2024', '34,199.68'),
            ('S81', '09/01/2024', '56,277.32'),
            ('S86', '08/26/2024', '56,277.31'),
            ('S87', '09/01/2024', '34,199.68'),
            ('U93', '08/28/2024', '34,199.68'),
            ('U94', '08/30/2024', '34,199.68'),
            ('U98', '08/30/2024', '34,199.68'),
            ('V99', '08/30/2024', '34,199.68'),
        ]

        # Get the Renaissance Condominium Association
        try:
            association = Association.objects.get(name='Renaissance Condominium Association')
        except Association.DoesNotExist:
            self.stdout.write(self.style.ERROR('Renaissance Condominium Association not found'))
            return

        success_count = 0
        error_count = 0

        for unit_number, payoff_date_str, payoff_amount_str in payoff_data:
            try:
                # Parse the date
                payoff_date = datetime.strptime(payoff_date_str, '%m/%d/%Y').date()

                # Parse the amount (remove commas and convert to Decimal)
                payoff_amount = Decimal(payoff_amount_str.replace(',', ''))

                # Find the unit
                try:
                    unit = Unit.objects.get(association=association, unit_number=unit_number)
                except Unit.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Unit {unit_number} not found'))
                    error_count += 1
                    continue

                # Get the unit assessment (should be only one special assessment)
                unit_assessments = UnitAssessment.objects.filter(unit=unit)

                if not unit_assessments.exists():
                    self.stdout.write(self.style.WARNING(f'No assessment found for unit {unit_number}'))
                    error_count += 1
                    continue

                # Update each unit assessment (usually just one)
                for unit_assessment in unit_assessments:
                    unit_assessment.payoff_amount = payoff_amount
                    unit_assessment.payoff_date = payoff_date
                    unit_assessment.is_paid_off = True
                    unit_assessment.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {unit_number}: ${payoff_amount} on {payoff_date}'
                        )
                    )
                    success_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing unit {unit_number}: {str(e)}')
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {success_count} units updated, {error_count} errors'
            )
        )
