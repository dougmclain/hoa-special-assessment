from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import date


def generate_assessment_summary_pdf(special_assessment):
    """Generate a PDF summary report for a special assessment"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6
    )

    # Title
    elements.append(Paragraph(f"{special_assessment.association.name}", title_style))
    elements.append(Paragraph(f"{special_assessment.name}", heading_style))
    elements.append(Spacer(1, 0.2*inch))

    # Loan Information Table
    loan_data = [
        ['Loan Information', ''],
        ['Total Loan Amount:', f'${special_assessment.total_loan_amount:,.2f}'],
        ['Interest Rate:', f'{special_assessment.interest_rate}%'],
        ['Loan Period:', f'{special_assessment.loan_period_months} months'],
        ['Monthly Loan Payment:', f'${special_assessment.monthly_loan_payment:,.2f}'],
        ['Start Date:', special_assessment.start_date.strftime('%B %d, %Y')],
    ]

    loan_table = Table(loan_data, colWidths=[2.5*inch, 2*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(loan_table)
    elements.append(Spacer(1, 0.3*inch))

    # Unit Assessments Table
    elements.append(Paragraph("Unit Assessment Details", heading_style))
    elements.append(Spacer(1, 0.1*inch))

    # Headers
    data = [['Unit', 'Base\nAssessment', 'LCE\nFees', 'Total\nAssessment',
             'Monthly\nBase', 'Monthly\nLCE', 'Total\nMonthly', 'Total\nPaid', 'Balance', 'Status']]

    # Add unit data
    for ua in special_assessment.unit_assessments.all():
        data.append([
            ua.unit.unit_number,
            f'${ua.base_assessment_amount:,.2f}',
            f'${ua.total_lce_fees():,.2f}',
            f'${ua.total_assessment_amount():,.2f}',
            f'${ua.monthly_base_payment:,.2f}',
            f'${ua.total_lce_monthly_payment():,.2f}',
            f'${ua.total_monthly_payment():,.2f}',
            f'${ua.total_paid():,.2f}',
            f'${ua.remaining_balance():,.2f}',
            ua.payment_status()
        ])

    # Add totals row
    total_base = sum(ua.base_assessment_amount for ua in special_assessment.unit_assessments.all())
    total_lce = sum(ua.total_lce_fees() for ua in special_assessment.unit_assessments.all())
    total_assessment = sum(ua.total_assessment_amount() for ua in special_assessment.unit_assessments.all())
    total_monthly_base = sum(ua.monthly_base_payment for ua in special_assessment.unit_assessments.all())
    total_monthly_lce = sum(ua.total_lce_monthly_payment() for ua in special_assessment.unit_assessments.all())
    total_monthly = sum(ua.total_monthly_payment() for ua in special_assessment.unit_assessments.all())
    total_paid = sum(ua.total_paid() for ua in special_assessment.unit_assessments.all())
    total_balance = sum(ua.remaining_balance() for ua in special_assessment.unit_assessments.all())

    data.append([
        'TOTALS',
        f'${total_base:,.2f}',
        f'${total_lce:,.2f}',
        f'${total_assessment:,.2f}',
        f'${total_monthly_base:,.2f}',
        f'${total_monthly_lce:,.2f}',
        f'${total_monthly:,.2f}',
        f'${total_paid:,.2f}',
        f'${total_balance:,.2f}',
        ''
    ])

    # Create table
    col_widths = [0.6*inch, 0.95*inch, 0.75*inch, 0.95*inch, 0.80*inch, 0.80*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.9*inch]
    unit_table = Table(data, colWidths=col_widths, repeatRows=1)

    # Style the table
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]

    # Alternate row colors
    for i in range(1, len(data) - 1):
        if i % 2 == 0:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))

    # Totals row styling
    table_style.extend([
        ('BACKGROUND', (0, len(data)-1), (-1, len(data)-1), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, len(data)-1), (-1, len(data)-1), colors.whitesmoke),
        ('FONTNAME', (0, len(data)-1), (-1, len(data)-1), 'Helvetica-Bold'),
    ])

    unit_table.setStyle(TableStyle(table_style))
    elements.append(unit_table)

    # Footer
    elements.append(Spacer(1, 0.2*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Generated on {date.today().strftime('%B %d, %Y')} | {special_assessment.association.management_company}", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_unit_statement_pdf(unit_assessment):
    """Generate a PDF statement for a specific unit"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    # Header
    elements.append(Paragraph(f"{unit_assessment.special_assessment.association.name}", title_style))
    elements.append(Paragraph(f"Unit {unit_assessment.unit.unit_number} - Assessment Statement", styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))

    # Assessment Details
    details_data = [
        ['Assessment Details', ''],
        ['Assessment Name:', unit_assessment.special_assessment.name],
        ['Unit Number:', unit_assessment.unit.unit_number],
        ['Owner Name:', unit_assessment.unit.owner_name or 'N/A'],
        ['Payment Option:', unit_assessment.get_payment_option_display()],
        ['Start Date:', unit_assessment.special_assessment.start_date.strftime('%B %d, %Y')],
    ]

    details_table = Table(details_data, colWidths=[2.5*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 0.3*inch))

    # Assessment Breakdown
    elements.append(Paragraph("Assessment Breakdown", styles['Heading3']))
    breakdown_data = [
        ['Description', 'Amount', 'Monthly Payment'],
        ['Base Assessment', f'${unit_assessment.base_assessment_amount:,.2f}', f'${unit_assessment.monthly_base_payment:,.2f}'],
    ]

    # Add LCE fees
    for fee in unit_assessment.additional_fees.all():
        breakdown_data.append([
            f'LCE: {fee.fee_type}',
            f'${fee.fee_amount:,.2f}',
            f'${fee.monthly_payment:,.2f}'
        ])

    breakdown_data.append([
        'TOTAL',
        f'${unit_assessment.total_assessment_amount():,.2f}',
        f'${unit_assessment.total_monthly_payment():,.2f}'
    ])

    breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(breakdown_table)
    elements.append(Spacer(1, 0.3*inch))

    # Payment Summary
    elements.append(Paragraph("Payment Summary", styles['Heading3']))
    summary_data = [
        ['Total Assessment:', f'${unit_assessment.total_assessment_amount():,.2f}'],
        ['Total Paid:', f'${unit_assessment.total_paid():,.2f}'],
        ['Remaining Balance:', f'${unit_assessment.remaining_balance():,.2f}'],
        ['Payment Status:', unit_assessment.payment_status()],
    ]

    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))

    # Payment History
    if unit_assessment.payments.exists():
        elements.append(Paragraph("Payment History", styles['Heading3']))
        payment_data = [['Date', 'Amount', 'Method', 'Reference']]

        for payment in unit_assessment.payments.all():
            payment_data.append([
                payment.payment_date.strftime('%m/%d/%Y'),
                f'${payment.amount:,.2f}',
                payment.payment_method or 'N/A',
                payment.reference_number or 'N/A'
            ])

        payment_table = Table(payment_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        elements.append(payment_table)

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Generated on {date.today().strftime('%B %d, %Y')}", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
