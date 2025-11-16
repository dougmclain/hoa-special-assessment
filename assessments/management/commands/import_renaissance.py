from django.core.management.base import BaseCommand
from assessments.models import Association, SpecialAssessment, Unit, UnitAssessment, AdditionalFee, MonthlyPaymentSchedule
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = 'Import Renaissance Condominium Association 2024 Special Assessment data'

    def calculate_monthly_lce(self, deck_amount, skylight_amount):
        """Calculate monthly LCE payment based on fee amounts from PDF"""
        monthly_lce = Decimal('0')

        # Skylight monthly payments
        if skylight_amount == Decimal('974.00'):
            monthly_lce += Decimal('9.01')
        elif skylight_amount == Decimal('487.00'):
            monthly_lce += Decimal('4.50')

        # Deck monthly payments
        if deck_amount == Decimal('23051.64'):
            monthly_lce += Decimal('213.23')
        elif deck_amount == Decimal('11525.82'):
            monthly_lce += Decimal('106.61')

        return monthly_lce

    def handle(self, *args, **kwargs):
        # Create Association
        association, created = Association.objects.get_or_create(
            name="Renaissance Condominium Association",
            defaults={
                'management_company': 'Dynamite Management',
                'address': ''
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created association: {association.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Association already exists: {association.name}'))

        # Create Special Assessment
        special_assessment, created = SpecialAssessment.objects.get_or_create(
            association=association,
            name="2024 Special Assessment",
            defaults={
                'total_loan_amount': Decimal('3500000.00'),
                'interest_rate': Decimal('8.38'),
                'loan_period_months': 240,
                'monthly_loan_payment': Decimal('30733.38'),
                'start_date': date(2024, 9, 1),
                'total_base_assessment': Decimal('3322567.98'),
                'total_lce_assessments': Decimal('177432.02'),
                'description': 'Reserve deficiency funding - 240 month payment plan at 8.38% interest'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created special assessment: {special_assessment.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Special assessment already exists: {special_assessment.name} - will update units and schedules'))

        # Unit data from PDF
        unit_data = [
            {'unit': 'A1', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'A2', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'A3', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'A4', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'A5', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'A6', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'A7', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'A8', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'B9', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'B10', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'C11', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'C12', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'C13', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'C14', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'C15', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'C16', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'C17', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'C18', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'D19', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'D20', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'E21', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'E22', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'E23', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'E24', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'E25', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'E26', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'E27', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'E28', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'F29', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'F30', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'G31', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'G32', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'G33', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'G34', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'G35', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'G36', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'G37', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'G38', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'H39', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'H40', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'J41', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'J42', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'J43', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'J44', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'J45', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'J46', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'J47', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'J48', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'K49', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'K50', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'L51', 'base': '33225.68', 'deck': '23051.64', 'skylight': '0'},
            {'unit': 'L52', 'base': '33225.68', 'deck': '11525.82', 'skylight': '0'},
            {'unit': 'L53', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'L54', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'L55', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'L56', 'base': '33225.68', 'deck': '23051.64', 'skylight': '0'},
            {'unit': 'L57', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'L58', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'M59', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'M60', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'N61', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'N62', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'N63', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'N64', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'N65', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'N66', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'N67', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'N68', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'P69', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'P70', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'Q71', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'Q72', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'Q73', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'Q74', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'Q75', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'Q76', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'Q77', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'Q78', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'R79', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'R80', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'S81', 'base': '33225.68', 'deck': '23051.64', 'skylight': '0'},
            {'unit': 'S82', 'base': '33225.68', 'deck': '11525.82', 'skylight': '0'},
            {'unit': 'S83', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'S84', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'S85', 'base': '33225.68', 'deck': '11525.82', 'skylight': '0'},
            {'unit': 'S86', 'base': '33225.68', 'deck': '23051.64', 'skylight': '0'},
            {'unit': 'S87', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'S88', 'base': '33225.68', 'deck': '0', 'skylight': '487.00'},
            {'unit': 'T89', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'T90', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'U91', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'U92', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'U93', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'U94', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'U95', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'U96', 'base': '33225.68', 'deck': '0', 'skylight': '0'},
            {'unit': 'U97', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'U98', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'V99', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
            {'unit': 'V100', 'base': '33225.68', 'deck': '0', 'skylight': '974.00'},
        ]

        # Create units and assessments
        count = 0
        BASE_MONTHLY = Decimal('290.92')  # Base monthly payment from PDF

        for data in unit_data:
            # Create unit
            unit, created = Unit.objects.get_or_create(
                association=association,
                unit_number=data['unit'],
                defaults={
                    'common_expense_allocation': Decimal('1.00')
                }
            )

            # Create unit assessment with manually set monthly payment from PDF
            deck_amt = Decimal(data['deck'])
            skylight_amt = Decimal(data['skylight'])

            unit_assessment, created = UnitAssessment.objects.get_or_create(
                unit=unit,
                special_assessment=special_assessment,
                defaults={
                    'base_assessment_amount': Decimal(data['base']),
                    'payment_option': 'monthly',
                    'monthly_base_payment': BASE_MONTHLY  # Use PDF value instead of calculated
                }
            )

            # Update monthly_base_payment if already exists
            if not created and unit_assessment.monthly_base_payment != BASE_MONTHLY:
                unit_assessment.monthly_base_payment = BASE_MONTHLY
                unit_assessment.save()

            # Create additional fees if applicable
            deck_monthly = Decimal('0')
            if deck_amt > 0:
                fee, fee_created = AdditionalFee.objects.get_or_create(
                    unit_assessment=unit_assessment,
                    fee_type='Deck',
                    defaults={
                        'fee_amount': deck_amt,
                        'description': 'Limited Common Element - Deck replacement/repair'
                    }
                )
                # Calculate monthly payment for deck
                if deck_amt == Decimal('23051.64'):
                    deck_monthly = Decimal('213.23')
                elif deck_amt == Decimal('11525.82'):
                    deck_monthly = Decimal('106.61')

                if fee.monthly_payment != deck_monthly:
                    fee.monthly_payment = deck_monthly
                    fee.save()

            skylight_monthly = Decimal('0')
            if skylight_amt > 0:
                fee, fee_created = AdditionalFee.objects.get_or_create(
                    unit_assessment=unit_assessment,
                    fee_type='Skylight',
                    defaults={
                        'fee_amount': skylight_amt,
                        'description': 'Limited Common Element - Skylight replacement/repair'
                    }
                )
                # Calculate monthly payment for skylight
                if skylight_amt == Decimal('974.00'):
                    skylight_monthly = Decimal('9.01')
                elif skylight_amt == Decimal('487.00'):
                    skylight_monthly = Decimal('4.50')

                if fee.monthly_payment != skylight_monthly:
                    fee.monthly_payment = skylight_monthly
                    fee.save()

            # Create monthly payment schedule (240 months starting 9/1/2024)
            total_monthly = BASE_MONTHLY + deck_monthly + skylight_monthly

            # Delete existing schedules if reimporting
            unit_assessment.monthly_schedule.all().delete()

            start_date = date(2024, 9, 1)
            for month_num in range(1, 241):  # 240 months
                due_date = start_date + relativedelta(months=month_num - 1)
                MonthlyPaymentSchedule.objects.create(
                    unit_assessment=unit_assessment,
                    due_date=due_date,
                    month_number=month_num,
                    expected_amount=total_monthly
                )

            count += 1
            if count % 10 == 0:
                self.stdout.write(f'Processed {count} units...')

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} units with 240-month payment schedules for Renaissance Condominium Association'))
