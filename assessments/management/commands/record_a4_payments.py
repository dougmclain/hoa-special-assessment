from django.core.management.base import BaseCommand
from assessments.models import Association, Unit, UnitAssessment, MonthlyPaymentSchedule
from datetime import date


class Command(BaseCommand):
    help = 'Record all 2024 monthly payments for unit A4 at Renaissance Condominium Association'

    def handle(self, *args, **options):
        # Get the Renaissance Condominium Association
        try:
            association = Association.objects.get(name='Renaissance Condominium Association')
        except Association.DoesNotExist:
            self.stdout.write(self.style.ERROR('Renaissance Condominium Association not found'))
            return

        # Find unit A4
        try:
            unit = Unit.objects.get(association=association, unit_number='A4')
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR('Unit A4 not found'))
            return

        # Get the unit assessment
        unit_assessments = UnitAssessment.objects.filter(unit=unit)
        if not unit_assessments.exists():
            self.stdout.write(self.style.ERROR('No assessment found for unit A4'))
            return

        unit_assessment = unit_assessments.first()

        # Get all monthly payment schedules for 2024
        schedules_2024 = MonthlyPaymentSchedule.objects.filter(
            unit_assessment=unit_assessment,
            due_date__year=2024
        ).order_by('due_date')

        if not schedules_2024.exists():
            self.stdout.write(self.style.WARNING('No payment schedules found for 2024'))
            return

        # Mark each payment as paid
        payment_count = 0
        for schedule in schedules_2024:
            schedule.paid_amount = schedule.expected_amount
            schedule.paid_date = schedule.due_date
            schedule.payment_method = 'Monthly Payment'
            schedule.notes = 'All 2024 payments recorded'
            schedule.save()
            payment_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Recorded payment for {schedule.due_date.strftime("%B %Y")}: ${schedule.expected_amount}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {payment_count} monthly payments recorded for unit A4 in 2024'
            )
        )

        # Show summary
        total_paid = sum(s.paid_amount for s in schedules_2024)
        self.stdout.write(
            self.style.SUCCESS(
                f'Total amount recorded: ${total_paid}'
            )
        )
