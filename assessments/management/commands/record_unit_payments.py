from django.core.management.base import BaseCommand
from assessments.models import Association, Unit, UnitAssessment, MonthlyPaymentSchedule
from datetime import date


class Command(BaseCommand):
    help = 'Record monthly payments for a specific unit and year'

    def add_arguments(self, parser):
        parser.add_argument('unit_number', type=str, help='Unit number (e.g., A4, B10)')
        parser.add_argument('--year', type=int, default=2024, help='Year to record payments for (default: 2024)')
        parser.add_argument('--association', type=str, default='Renaissance Condominium Association',
                          help='Association name')

    def handle(self, *args, **options):
        unit_number = options['unit_number']
        year = options['year']
        association_name = options['association']

        # Get the association
        try:
            association = Association.objects.get(name=association_name)
        except Association.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'{association_name} not found'))
            return

        # Find the unit
        try:
            unit = Unit.objects.get(association=association, unit_number=unit_number)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Unit {unit_number} not found'))
            return

        # Get the unit assessment
        unit_assessments = UnitAssessment.objects.filter(unit=unit)
        if not unit_assessments.exists():
            self.stdout.write(self.style.ERROR(f'No assessment found for unit {unit_number}'))
            return

        unit_assessment = unit_assessments.first()

        # Get all monthly payment schedules for the specified year
        schedules = MonthlyPaymentSchedule.objects.filter(
            unit_assessment=unit_assessment,
            due_date__year=year
        ).order_by('due_date')

        if not schedules.exists():
            self.stdout.write(self.style.WARNING(f'No payment schedules found for {year}'))
            return

        # Mark each payment as paid
        payment_count = 0
        for schedule in schedules:
            schedule.paid_amount = schedule.expected_amount
            schedule.paid_date = schedule.due_date
            schedule.payment_method = 'Monthly Payment'
            schedule.notes = f'All {year} payments recorded'
            schedule.save()
            payment_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Recorded payment for {schedule.due_date.strftime("%B %Y")}: ${schedule.expected_amount}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {payment_count} monthly payments recorded for unit {unit_number} in {year}'
            )
        )

        # Show summary
        total_paid = sum(s.paid_amount for s in schedules)
        self.stdout.write(
            self.style.SUCCESS(
                f'Total amount recorded: ${total_paid}'
            )
        )
