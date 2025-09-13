# ScholarIQ - AI-powered Student Analytics Platform

ScholarIQ is a FastAPI-based backend service that provides AI-powered analytics for student performance tracking and educational insights.

## Features

- **FastAPI** for high-performance API development
- **SQLAlchemy** with async support for database operations
- **Pydantic** for data validation and settings management
- **JWT-based authentication** (to be implemented)
- **Structured logging** with JSON formatting
- **CORS** enabled for frontend integration
- **Environment-based configuration**
- **Unit tests** with pytest

## Prerequisites

- Python 3.9+
- PostgreSQL (or SQLite for development)
- pip (Python package manager)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/keshavgujrathi/scholariq.git
cd scholariq
```

### 2. Set up a virtual environment

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your configuration.

### 5. Initialize the database

```bash
# For development with SQLite (default)
python -m app.core.database

# For production with PostgreSQL
# Make sure to set DATABASE_URL in .env first
```

### 6. Run the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Project Structure

```
scholariq/
├── app/                       # Application package
│   ├── api/                   # API routes
│   │   └── api_v1/            # API version 1
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database configuration
│   │   └── logging.py         # Logging configuration
│   ├── models/                # Database models
│   │   ├── base.py            # Base model class
│   │   └── __init__.py
│   └── schemas/               # Pydantic models
├── data/                      # Data files and uploads
├── tests/                     # Test files
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # This file
└── requirements.txt           # Project dependencies
```

## API Documentation

Once the application is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative API docs**: `http://localhost:8000/redoc`
- **Health check**: `http://localhost:8000/health`

## Running Tests

```bash
pytest
```

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for static type checking

Run the following commands before committing:

```bash
black .
isort .
mypy .
```

## Deployment

For production deployment, consider using:

- **Gunicorn** with Uvicorn workers
- **Nginx** as a reverse proxy
- **PostgreSQL** for the database
- **Docker** for containerization (recommended)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
