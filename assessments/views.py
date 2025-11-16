from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from django.db.models import Sum, Count
from django.contrib import messages
from .models import Association, SpecialAssessment, Unit, UnitAssessment, Payment, MonthlyPaymentSchedule, AdditionalFee
from .reports import generate_assessment_summary_pdf, generate_unit_statement_pdf
from decimal import Decimal
from datetime import datetime, date


def home(request):
    """Home page showing all associations"""
    associations = Association.objects.all()
    return render(request, 'assessments/home.html', {
        'associations': associations
    })


def association_detail(request, association_id):
    """Detail view for an association"""
    association = get_object_or_404(Association, pk=association_id)
    assessments = association.special_assessments.all()

    return render(request, 'assessments/association_detail.html', {
        'association': association,
        'assessments': assessments
    })


def assessment_detail(request, assessment_id):
    """Detail view for a special assessment"""
    assessment = get_object_or_404(SpecialAssessment, pk=assessment_id)
    unit_assessments = assessment.unit_assessments.all()

    # Calculate totals
    total_assessment = sum(ua.total_assessment_amount() for ua in unit_assessments)
    total_paid = sum(ua.total_paid() for ua in unit_assessments)
    total_remaining = sum(ua.remaining_balance() for ua in unit_assessments)

    # Status breakdown
    status_counts = {}
    for ua in unit_assessments:
        status = ua.payment_status()
        status_counts[status] = status_counts.get(status, 0) + 1

    return render(request, 'assessments/assessment_detail.html', {
        'assessment': assessment,
        'unit_assessments': unit_assessments,
        'total_assessment': total_assessment,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'status_counts': status_counts
    })


def unit_assessment_detail(request, unit_assessment_id):
    """Detail view for a unit assessment"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)
    additional_fees = unit_assessment.additional_fees.all()
    payments = unit_assessment.payments.all()

    return render(request, 'assessments/unit_assessment_detail.html', {
        'unit_assessment': unit_assessment,
        'additional_fees': additional_fees,
        'payments': payments
    })


def download_assessment_pdf(request, assessment_id):
    """Generate and download PDF for special assessment"""
    assessment = get_object_or_404(SpecialAssessment, pk=assessment_id)
    pdf_buffer = generate_assessment_summary_pdf(assessment)

    filename = f"{assessment.association.name}_{assessment.name}.pdf".replace(" ", "_")
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


def download_unit_statement_pdf(request, unit_assessment_id):
    """Generate and download PDF statement for a unit"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)
    pdf_buffer = generate_unit_statement_pdf(unit_assessment)

    filename = f"Unit_{unit_assessment.unit.unit_number}_Statement.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


def monthly_payments(request, unit_assessment_id):
    """View and enter monthly payments for a unit"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)

    # Handle payment entry
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        paid_amount = request.POST.get('paid_amount')
        paid_date = request.POST.get('paid_date')
        payment_method = request.POST.get('payment_method', '')
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')

        if schedule_id and paid_amount:
            schedule = get_object_or_404(MonthlyPaymentSchedule, pk=schedule_id)
            schedule.paid_amount = Decimal(paid_amount)
            if paid_date:
                schedule.paid_date = datetime.strptime(paid_date, '%Y-%m-%d').date()
            schedule.payment_method = payment_method
            schedule.reference_number = reference_number
            schedule.notes = notes
            schedule.save()
            messages.success(request, f'Payment recorded for {schedule.due_date.strftime("%B %Y")}')
            return redirect('assessments:monthly_payments', unit_assessment_id=unit_assessment_id)

    # Get all monthly schedules
    monthly_schedules = unit_assessment.monthly_schedule.all().order_by('due_date')

    # Group by year for better organization
    schedules_by_year = {}
    for schedule in monthly_schedules:
        year = schedule.due_date.year
        if year not in schedules_by_year:
            schedules_by_year[year] = []
        schedules_by_year[year].append(schedule)

    return render(request, 'assessments/monthly_payments.html', {
        'unit_assessment': unit_assessment,
        'schedules_by_year': schedules_by_year,
        'today': date.today()
    })


def adjust_unit_assessment(request, unit_assessment_id):
    """Adjust unit assessment amounts"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)

    if request.method == 'POST':
        # Update base assessment
        base_assessment = request.POST.get('base_assessment')
        if base_assessment:
            unit_assessment.base_assessment_amount = Decimal(base_assessment)
            unit_assessment.save()
            messages.success(request, 'Base assessment updated successfully')

        # Update or delete existing fees
        for fee in unit_assessment.additional_fees.all():
            fee_amount = request.POST.get(f'fee_amount_{fee.id}')
            delete_fee = request.POST.get(f'delete_fee_{fee.id}')

            if delete_fee:
                fee.delete()
                messages.success(request, f'{fee.fee_type} fee deleted')
            elif fee_amount:
                fee.fee_amount = Decimal(fee_amount)
                fee.save()
                messages.success(request, f'{fee.fee_type} fee updated')

        # Add new fee if specified
        new_fee_type = request.POST.get('new_fee_type')
        new_fee_amount = request.POST.get('new_fee_amount')
        if new_fee_type and new_fee_amount:
            AdditionalFee.objects.create(
                unit_assessment=unit_assessment,
                fee_type=new_fee_type,
                fee_amount=Decimal(new_fee_amount)
            )
            messages.success(request, f'New {new_fee_type} fee added')

        # Recreate monthly schedules with new amounts
        unit_assessment.monthly_schedule.all().delete()
        total_monthly = unit_assessment.total_monthly_payment()
        start_date = unit_assessment.special_assessment.start_date

        from dateutil.relativedelta import relativedelta
        for month_num in range(1, 241):
            due_date = start_date + relativedelta(months=month_num - 1)
            MonthlyPaymentSchedule.objects.create(
                unit_assessment=unit_assessment,
                due_date=due_date,
                month_number=month_num,
                expected_amount=total_monthly
            )

        messages.success(request, 'Monthly payment schedules updated')
        return redirect('assessments:unit_assessment_detail', unit_assessment_id=unit_assessment_id)

    return render(request, 'assessments/adjust_unit_assessment.html', {
        'unit_assessment': unit_assessment,
        'additional_fees': unit_assessment.additional_fees.all()
    })


def payoff_calculator(request, unit_assessment_id):
    """Calculate and record payoff amounts"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)

    # Handle payoff recording
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'record_payoff':
            payoff_amount = request.POST.get('payoff_amount')
            payoff_date = request.POST.get('payoff_date')

            if payoff_amount and payoff_date:
                unit_assessment.payoff_amount = Decimal(payoff_amount)
                unit_assessment.payoff_date = datetime.strptime(payoff_date, '%Y-%m-%d').date()

                # Check if fully paid off
                remaining = unit_assessment.calculate_payoff_amount()
                if remaining <= 0:
                    unit_assessment.is_paid_off = True

                unit_assessment.save()
                messages.success(request, f'Payoff amount of {payoff_amount} recorded')
                return redirect('assessments:payoff_calculator', unit_assessment_id=unit_assessment_id)

        elif action == 'calculate':
            calc_date = request.POST.get('calculation_date')
            if calc_date:
                calc_date_obj = datetime.strptime(calc_date, '%Y-%m-%d').date()
                calculated_payoff = unit_assessment.calculate_payoff_amount(calc_date_obj)
                return render(request, 'assessments/payoff_calculator.html', {
                    'unit_assessment': unit_assessment,
                    'calculated_payoff': calculated_payoff,
                    'calculation_date': calc_date_obj,
                    'today': date.today()
                })

    # Calculate current payoff amount
    current_payoff = unit_assessment.calculate_payoff_amount()

    return render(request, 'assessments/payoff_calculator.html', {
        'unit_assessment': unit_assessment,
        'current_payoff': current_payoff,
        'today': date.today()
    })


def edit_payoff(request, unit_assessment_id):
    """Edit existing payoff information"""
    unit_assessment = get_object_or_404(UnitAssessment, pk=unit_assessment_id)

    if request.method == 'POST':
        payoff_amount = request.POST.get('payoff_amount')
        payoff_date = request.POST.get('payoff_date')
        is_paid_off = request.POST.get('is_paid_off') == 'on'

        # Handle clearing payoff
        if request.POST.get('clear_payoff'):
            unit_assessment.payoff_amount = Decimal('0.00')
            unit_assessment.payoff_date = None
            unit_assessment.is_paid_off = False
            unit_assessment.save()
            messages.success(request, 'Payoff information cleared')
            return redirect('assessments:unit_assessment_detail', unit_assessment_id=unit_assessment_id)

        # Update payoff information
        if payoff_amount:
            unit_assessment.payoff_amount = Decimal(payoff_amount.replace(',', ''))
        else:
            unit_assessment.payoff_amount = Decimal('0.00')

        if payoff_date:
            unit_assessment.payoff_date = datetime.strptime(payoff_date, '%Y-%m-%d').date()
        else:
            unit_assessment.payoff_date = None

        unit_assessment.is_paid_off = is_paid_off
        unit_assessment.save()

        messages.success(request, 'Payoff information updated successfully')
        return redirect('assessments:unit_assessment_detail', unit_assessment_id=unit_assessment_id)

    return render(request, 'assessments/edit_payoff.html', {
        'unit_assessment': unit_assessment,
    })


def payment_report_2024(request, assessment_id):
    """Generate 2024 payment report for an assessment"""
    assessment = get_object_or_404(SpecialAssessment, pk=assessment_id)

    # Get all unit assessments for this special assessment
    unit_assessments = assessment.unit_assessments.select_related('unit').order_by('unit__unit_number')

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
                })

        # Check 2024 monthly payments
        from assessments.models import MonthlyPaymentSchedule
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
                })

    # Calculate totals
    payoff_total = sum(u['amount'] for u in payoff_units)
    monthly_total = sum(u['amount'] for u in monthly_paid_units)
    grand_total = payoff_total + monthly_total
    total_units = len(payoff_units) + len(monthly_paid_units)

    return render(request, 'assessments/payment_report_2024.html', {
        'assessment': assessment,
        'payoff_units': payoff_units,
        'monthly_paid_units': monthly_paid_units,
        'payoff_total': payoff_total,
        'monthly_total': monthly_total,
        'grand_total': grand_total,
        'total_units': total_units,
        'report_date': date(2024, 12, 31),
    })
