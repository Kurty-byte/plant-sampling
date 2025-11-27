# Plant Sampling Research Database

A comprehensive Django-based web application for managing plant sampling research data. This application provides a complete CRUD interface for collecting, storing, and analyzing environmental and biological data from plant sampling expeditions.

## Features

- Complete Plant Sampling Management: Create, read, update, and delete plant samples with full environmental data
- Researcher Management: Link researchers to samples with role assignments
- Location Tracking: Store geographic sampling locations with coordinates
- Environmental Conditions: Record temperature, humidity, soil composition, and other environmental factors
- Growth Metrics: Track plant growth over time with height, leaf count, and health status
- Audit Logging: Complete audit trail for all data modifications
- Soft/Hard Delete: Safe data preservation with permanent deletion options
- REST API: Full RESTful API for programmatic access
- Web Interface: User-friendly web interface with tabbed navigation

## Architecture

- Backend: Django 5.2.8 with Django REST Framework
- Database: PostgreSQL with JSONB fields for flexible data storage
- Frontend: HTML5, CSS3, Vanilla JavaScript
- API: RESTful endpoints with comprehensive serialization

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git
- Virtual environment (recommended)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Activity9-v4
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create a PostgreSQL database named `plant_sampling_db` with the credentials specified in `.env`.

### 5. Environment Configuration

The `.env` file is already configured with default values:

```env
POSTGRES_DB=plant_sampling_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=319722195
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Modify these values if your database configuration differs.

### 6. Database Migration

```bash
cd plant_sampling
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run the Application

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Database Schema

The application uses a comprehensive PostgreSQL schema with the following main tables:

- sampling_location: Geographic locations with coordinates and metadata
- environmental_conditions: Environmental parameters (temperature, humidity, soil composition)
- researcher_info: Researcher contact information and affiliations
- plant_sample: Main sample records linking location, conditions, and researchers
- sample_researchers: Junction table for researcher-sample relationships
- growth_metrics: Time-series data for plant growth tracking
- sample_audit_log: Complete audit trail for data modifications

See `schema.sql` for the complete database schema with constraints and indexes.

## API Endpoints

### Core Resources

- `GET/POST /api/locations/` - Sampling locations
- `GET/POST /api/conditions/` - Environmental conditions
- `GET/POST /api/researchers/` - Researcher information
- `GET /api/samples/` - List all samples
- `POST /api/samples/create/` - Create new sample
- `GET /api/samples/{id}/` - Get sample details
- `PUT /api/samples/{id}/update/` - Update sample
- `DELETE /api/samples/{id}/` - Soft delete sample
- `DELETE /api/samples/{id}/hard-delete/` - Permanently delete sample

### Additional Endpoints

- `GET/POST /api/sample-researchers/` - Researcher-sample links
- `GET/POST /api/growth-metrics/` - Growth measurements
- `GET /api/audit-logs/` - Audit log entries
- `GET /api/` - API root with endpoint documentation

## Usage

### Web Interface

1. Add Data: Use the tabbed interface to add locations, researchers, and complete plant samples
2. Query Samples: Search for samples by ID to view complete data
3. Update Samples: Load existing samples, modify data, and save changes
4. Delete Samples: Choose between soft delete (preserves data) or hard delete (permanent removal)

### API Usage

```python
import requests

# Get all samples
response = requests.get('http://127.0.0.1:8000/api/samples/')
samples = response.json()

# Create a new sample
sample_data = {
    "sample_detail": {
        "species": "Quercus rubra",
        "common_name": "Northern Red Oak",
        "sampling_date": "2025-11-27"
    },
    "location": 1,
    "condition": 1
}
response = requests.post('http://127.0.0.1:8000/api/samples/create/', json=sample_data)
```

## Project Structure

```
Activity9-v4/
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── schema.sql             # Database schema
├── schema.dbml            # Database markup language
├── plant_sampling/        # Django project
│   ├── manage.py
│   ├── config/            # Project configuration
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       └── sampling/      # Main application
│           ├── models.py      # Database models
│           ├── views.py       # API views
│           ├── serializers.py # Data serialization
│           ├── urls.py        # URL routing
│           ├── admin.py       # Django admin
│           ├── apps.py
│           ├── tests.py
│           ├── migrations/    # Database migrations
│           ├── static/        # Static files (CSS/JS)
│           └── templates/     # HTML templates
│               ├── base.html
│               ├── home.html
│               └── includes/  # Template includes
└── .venv/               # Virtual environment
```

## Development

### Running Tests

```bash
cd plant_sampling
python manage.py test
```

### Code Formatting

```bash
# Install development dependencies
pip install black isort flake8

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Management

```bash
# Create new migration
python manage.py makemigrations sampling

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush
```

## Data Validation

The application includes comprehensive data validation:

- Geographic coordinates: Latitude (-90 to 90), Longitude (-180 to 180)
- Environmental ranges: Temperature (-50°C to 60°C), Humidity (0-100%), Altitude (-500m to 9000m)
- Soil pH: 0-14 range
- Email validation: Proper email format checking
- Required fields: Species, common name, sampling date, location, conditions
- Unique constraints: Researcher emails, sample-researcher relationships

## Security Features

- CSRF protection on all forms
- SQL injection prevention through Django ORM
- Input validation and sanitization
- CORS headers configured for API access
- Secure password handling (for admin interface)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**Database Connection Error**
- Ensure PostgreSQL is running
- Check `.env` file credentials
- Verify database exists

**Migration Errors**
- Run `python manage.py migrate --fake-initial` if needed
- Check migration files for conflicts

**Static Files Not Loading**
- Run `python manage.py collectstatic` for production
- Ensure `DEBUG=True` in development

**API Authentication Issues**
- Check CORS settings in `settings.py`
- Verify API endpoint URLs

## Support

For questions or issues, please create an issue in the repository or contact the development team.

---

Built with Django, PostgreSQL, and modern web technologies.