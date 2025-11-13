from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.db.models import Sum, Count
from .models import Association, SpecialAssessment, Unit, UnitAssessment, Payment
from .reports import generate_assessment_summary_pdf, generate_unit_statement_pdf
from decimal import Decimal


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
