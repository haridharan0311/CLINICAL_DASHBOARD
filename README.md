# Clinical Dashboard

A full-stack clinical dashboard system designed to manage healthcare data for clinics in Tamil Nadu. The system consists of a Django REST API backend and a React/Vite frontend, providing analytics, patient management, pharmacy operations, and role-based access control for healthcare professionals.

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

### Backend
- **Framework**: Django 6.0.4
- **API Framework**: Django REST Framework 3.17.1
- **Database**: SQLite (development) / MySQL (production-ready)
- **Authentication**: Django's built-in auth system with custom User model
- **Data Processing**: Pandas for analytics (implied in services)
- **Deployment Ready**: ASGI/WSGI support

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS
- **State Management**: React Context API
- **HTTP Client**: Axios (implied in services)

## Project Structure

```
Clinical_Dashboard/
├── backend/                     # Django REST API Backend
│   ├── config/                  # Django project settings
│   ├── api/                     # REST API endpoints and serializers
│   ├── users/                   # Custom user model and authentication
│   ├── clinical/                # Patient, doctor, clinic, appointment models
│   ├── pharmacy/                # Drug, prescription management
│   ├── analytics/               # Alert system and analytics services
│   └── data/                    # CSV data files for seeding
├── frontend/                    # React/Vite Frontend
│   ├── public/                  # Static assets
│   └── src/
│       ├── components/          # Reusable UI components
│       ├── pages/               # Page components
│       ├── services/            # API service functions
│       ├── context/             # React context providers
│       ├── hooks/               # Custom React hooks
│       ├── utils/               # Utility functions
│       ├── assets/              # Images, icons, etc.
│       ├── App.jsx              # Main App component
│       └── main.jsx             # Entry point
└── data/                        # Root data directory (shared)
    ├── analytics_alert.csv
    ├── clinical_appointment.csv
    ├── clinical_clinic.csv
    ├── clinical_disease.csv
    ├── clinical_doctor.csv
    ├── clinical_patient.csv
    ├── pharmacy_drugbatch.csv
    ├── pharmacy_drugmaster.csv
    ├── pharmacy_prescription.csv
    ├── pharmacy_prescriptionline.csv
    ├── users_auditlog.csv
    └── users_user.csv
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- pip package manager
- npm or yarn
- Git

### Setup Steps

#### 1. Clone the repository
```bash
git clone <repository-url>
cd Clinical_Dashboard
```

#### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Run database migrations
python manage.py migrate

# Seed the database with sample data
python manage.py seed_data

# Create superuser (optional)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend will be available at `http://localhost:5173/` (or similar)

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
# Backend tests
cd backend
python manage.py test

# Frontend tests (when implemented)
cd ../frontend
npm test
```

### Code Style
- **Backend**: Follow Django best practices and Django REST Framework conventions
- **Frontend**: Follow React best practices with proper separation of concerns

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
- Use proper WSGI server (Gunicorn) for backend
- Configure proper web server (nginx) for frontend
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

- Real-time notifications
- Advanced ML models for predictions
- Mobile app API
- Integration with external healthcare systems
- Multi-language support
- Enhanced UI/UX with charts and graphs
- Telemedicine features
- Insurance integration