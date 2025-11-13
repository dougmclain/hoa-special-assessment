# HOA Special Assessment Tracker

A Django-based web application for tracking and managing special assessments for Homeowners Associations (HOAs). This application supports flexible payment terms, interest calculations, payment tracking, and comprehensive reporting.

## Features

- **Flexible Assessment Management**: Support for different assessment amounts per unit with customizable Limited Common Element (LCE) fees
- **Payment Options**: Lump sum or monthly payment plans with interest calculations
- **Interest Calculation**: Automatic calculation of monthly payments using loan amortization formulas
- **Payment Tracking**: Record and track payments for each unit
- **Additional Fees**: Add custom fees (Deck, Skylight, etc.) to specific units
- **Payoff Calculations**: Calculate remaining balance and payoff amounts at any time
- **PDF Reports**: Generate professional PDF reports for entire assessments or individual units
- **Excel Export**: Export assessment data to Excel spreadsheets
- **Web Interface**: User-friendly interface for viewing assessments and unit details
- **Admin Panel**: Comprehensive Django admin interface for data management

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (easily upgradable to PostgreSQL, MySQL, etc.)
- **PDF Generation**: ReportLab
- **Excel Export**: openpyxl
- **Python**: 3.11+

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository** (or download the code):
   ```bash
   cd hoa-special-assessment
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (if not already done):
   ```bash
   python manage.py migrate
   ```

5. **Import Renaissance Condominium data** (optional):
   ```bash
   python manage.py import_renaissance
   ```

6. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main website: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Admin Panel

The admin panel provides full access to all data management features:

1. **Access**: Navigate to http://127.0.0.1:8000/admin/ and log in with your superuser credentials

2. **Manage Associations**:
   - Add new HOAs/Condo Associations
   - Edit association details

3. **Create Special Assessments**:
   - Set loan amount, interest rate, and payment period
   - Define start date and description

4. **Add Units**:
   - Create unit records with owner information
   - Set common expense allocation

5. **Configure Unit Assessments**:
   - Link units to special assessments
   - Set base assessment amounts
   - Choose payment option (lump sum or monthly)
   - Add Limited Common Element fees

6. **Record Payments**:
   - Track payments received from unit owners
   - Record payment method and reference numbers
   - Add notes for each payment

7. **Generate Reports**:
   - Export entire assessment to Excel (select assessment and use action dropdown)
   - Download PDF reports from the admin or web interface

### Web Interface

The web interface provides a clean view of assessments and units:

1. **Home Page**: View all associations
2. **Association Details**: View special assessments for each association
3. **Assessment Details**: View all units and their payment status
4. **Unit Details**: View individual unit assessment and payment history

### PDF Reports

Two types of PDF reports are available:

1. **Assessment Summary Report**: Complete overview of all units in an assessment
   - Loan information
   - All unit assessments with payment status
   - Totals and summary

2. **Unit Statement**: Individual unit statement
   - Unit-specific assessment details
   - Payment breakdown
   - Payment history

### Excel Export

Excel exports include:
- Assessment summary information
- Complete unit list with all amounts
- Payment status for each unit
- Formatted and ready for analysis

## Data Models

The application uses the following core models:

- **Association**: HOA or Condominium Association
- **SpecialAssessment**: A special assessment project with loan terms
- **Unit**: Individual unit/home in the association
- **UnitAssessment**: Links a unit to a special assessment with specific amounts
- **AdditionalFee**: Limited Common Element fees (Deck, Skylight, etc.)
- **Payment**: Payment records for each unit

## Interest Calculation

The application uses standard loan amortization formulas:

- **Monthly Payment**: `M = P * [r(1+r)^n] / [(1+r)^n - 1]`
  - M = Monthly payment
  - P = Principal amount
  - r = Monthly interest rate (annual rate / 12)
  - n = Number of months

- **Payoff Amount**: Present value of remaining payments

## Sample Data

The application includes a management command to import the Renaissance Condominium Association data from the included PDF:

```bash
python manage.py import_renaissance
```

This creates:
- Renaissance Condominium Association
- 2024 Special Assessment ($3.5M, 8.38%, 240 months)
- 100 units (A1 through V100)
- Base assessments and LCE fees from the PDF

## Development

### Project Structure

```
hoa-special-assessment/
├── assessments/              # Main application
│   ├── models.py            # Data models
│   ├── admin.py             # Admin interface
│   ├── views.py             # Web views
│   ├── urls.py              # URL routing
│   ├── reports.py           # PDF generation
│   ├── templates/           # HTML templates
│   └── management/          # Management commands
├── hoa_management/          # Django project settings
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Extending the Application

To add new features:

1. **New Assessment Type**: Modify `SpecialAssessment` model or create new model
2. **Custom Calculations**: Add methods to model classes
3. **New Reports**: Create functions in `reports.py`
4. **Additional Views**: Add views and templates as needed

## Production Deployment

For production use:

1. Change `DEBUG = False` in settings.py
2. Set a secure `SECRET_KEY`
3. Configure proper database (PostgreSQL recommended)
4. Set up static file serving
5. Use a production web server (Gunicorn, uWSGI)
6. Configure HTTPS
7. Set up regular backups

## Support

For questions or issues with the application:
1. Check the Django documentation: https://docs.djangoproject.com/
2. Review the code comments and docstrings
3. Check the admin panel help text

## License

This project is provided as-is for use by Dynamite Management and associated HOAs.

## Credits

- Built with Django and Python
- PDF generation by ReportLab
- Excel export by openpyxl
- Developed for Dynamite Management
