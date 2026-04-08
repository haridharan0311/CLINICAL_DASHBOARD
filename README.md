# Clinical Dashboard Backend

A comprehensive Django REST API backend for a clinical dashboard system designed to manage healthcare data for clinics in Tamil Nadu. The system provides analytics, patient management, pharmacy operations, and role-based access control for healthcare professionals.

## Features

### Core Functionality
- **User Management**: Role-based authentication with Super Admin, Clinic Admin, Doctor, and Pharmacist roles
- **Clinic Management**: Multi-clinic support with location data and capacity tracking
- **Patient Records**: Comprehensive patient information including demographics and medical history
- **Appointment System**: Doctor-patient appointment scheduling with vitals tracking
- **Pharmacy Management**: Drug inventory, prescriptions, and automated restock suggestions
- **Disease Tracking**: ICD-10 coded disease database with seasonality and severity information

### Analytics & Insights
- **Disease Trend Analysis**: Historical disease patterns and case tracking
- **Spike Detection**: Automated outbreak detection with configurable thresholds
- **Restock Predictions**: AI-powered medicine demand forecasting
- **Alert System**: Real-time notifications for critical events (disease spikes, low stock)
- **CSV Export**: Data export functionality for reporting and analysis

### Security & Access Control
- JWT-based authentication
- Role-based permissions (RBAC)
- Clinic-level data isolation
- CORS support for frontend integration

## Tech Stack

- **Backend Framework**: Django 6.0.4
- **API Framework**: Django REST Framework 3.17.1
- **Database**: SQLite (development) / MySQL (production-ready)
- **Authentication**: Django's built-in auth system with custom User model
- **Data Processing**: Pandas for analytics (implied in services)
- **Deployment Ready**: ASGI/WSGI support

## Project Structure

```
backend/
├── config/                 # Django project settings
├── api/                    # REST API endpoints and serializers
├── users/                  # Custom user model and authentication
├── clinical/               # Patient, doctor, clinic, appointment models
├── pharmacy/               # Drug, prescription management
├── analytics/              # Alert system and analytics services
└── data/                   # CSV data files for seeding
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Clinical_Dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to backend directory**
   ```bash
   cd backend
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed the database with sample data**
   ```bash
   python manage.py seed_data
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication
- `POST /admin/login/` - Django admin login
- Role-based access control implemented across all endpoints

### Analytics API (`/api/`)
- `GET /api/disease-trends/` - Get disease trend data
  - Query params: `days` (default: 30), `clinic_id` (for Super Admin)
- `GET /api/spike-detection/` - Get active alerts
- `POST /api/spike-detection/` - Trigger manual spike detection
- `GET /api/restock-suggestions/` - Get low-stock drugs with predictions
- `GET /api/export/` - Export data as CSV
  - Query params: `type` (trends/restock), `clinic_id`

### Admin Interface
- `/admin/` - Django admin panel for data management

## Data Models

### Clinical
- **Clinic**: Location, capacity, contact information
- **Doctor**: User profile, specialization, clinic assignment
- **Patient**: Demographics, medical history
- **Disease**: ICD-10 codes, categories, seasonality
- **Appointment**: Visit records with vitals and outcomes

### Pharmacy
- **DrugMaster**: Inventory, pricing, prescription requirements
- **Prescription**: Doctor orders with duration
- **PrescriptionLine**: Individual medication details

### Analytics
- **AnalyticsAlert**: Automated alerts for spikes and low stock

## User Roles & Permissions

- **Super Admin**: Full system access, can view all clinics
- **Clinic Admin**: Clinic-specific management
- **Doctor**: Patient care, appointment management
- **Pharmacist**: Pharmacy operations, prescription filling

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
- Follow Django best practices
- Use Django REST Framework conventions
- Maintain proper separation of concerns (models, views, serializers, services)

### Database Seeding
The system includes a comprehensive seeding command that loads Tamil Nadu healthcare data from CSV files:
- Clinics, doctors, patients
- Disease database
- Pharmacy inventory
- Sample appointments and prescriptions
- Analytics alerts

## Deployment

### Production Considerations
- Switch to MySQL/PostgreSQL database
- Configure proper SECRET_KEY
- Set DEBUG=False
- Configure ALLOWED_HOSTS
- Use proper WSGI server (Gunicorn)
- Set up static file serving
- Configure CORS properly

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=mysql://user:pass@host:port/db
ALLOWED_HOSTS=yourdomain.com
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Future Enhancements

- Frontend dashboard implementation
- Real-time notifications
- Advanced ML models for predictions
- Mobile app API
- Integration with external healthcare systems
- Multi-language support</content>
<parameter name="filePath">E:\technospice\project_2\Clinical_Dashboard\README.md

