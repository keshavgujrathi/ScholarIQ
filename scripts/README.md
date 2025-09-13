# Database Management Scripts

This directory contains scripts for managing the ScholarIQ database.

## Available Scripts

### `manage_db.py`

A command-line utility for managing the database.

**Usage:**
```bash
python -m scripts.manage_db <command>
```

**Available Commands:**
- `create` - Create the database if it doesn't exist
- `drop` - Drop the database (DANGER: deletes all data)
- `init` - Initialize the database (create tables)
- `migrate` - Run database migrations
- `seed` - Seed the database with initial data
- `reset` - Reset the database (drop, create, migrate, seed)

**Examples:**
```bash
# Initialize the database
python -m scripts.manage_db init

# Run migrations
python -m scripts.manage_db migrate

# Seed the database
python -m scripts.manage_db seed

# Reset the database (DANGER: deletes all data)
python -m scripts.manage_db reset
```

### `seed_database.py`

Script for populating the database with initial data.

**Usage:**
```bash
python -m scripts.seed_database
```

## Initial Setup

1. **Install Dependencies**
   Make sure you have all the required Python packages installed:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Configure Environment**
   Copy the example environment file and update it with your database credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. **Initialize the Database**
   ```bash
   python -m scripts.manage_db init
   ```

4. **Run Migrations**
   ```bash
   python -m scripts.manage_db migrate
   ```

5. **Seed the Database (Optional)**
   ```bash
   python -m scripts.manage_db seed
   ```

## Database Schema

The database schema is defined using SQLAlchemy models in `app/db/models.py`. The main tables include:

- `users` - User accounts
- `roles` - User roles and permissions
- `analyses` - Analysis jobs and results
- `contents` - Content being analyzed
- `analysis_results` - Detailed analysis results
- `api_keys` - API keys for authentication
- `audit_logs` - System audit trail
- `system_settings` - Application configuration

## Adding Migrations

To create a new database migration:

1. Install Alembic if not already installed:
   ```bash
   pip install alembic
   ```

2. Generate a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

3. Review the generated migration file in `alembic/versions/`

4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Best Practices

- Always create a new migration when making changes to the database schema
- Test migrations in a development environment before applying to production
- Back up your database before running destructive operations
- Use transactions for data integrity when making multiple related changes
- Keep migration files in version control

## Troubleshooting

### Database Connection Issues
- Verify your database server is running
- Check the connection string in your `.env` file
- Ensure your database user has the necessary permissions

### Migration Issues
- If a migration fails, check the error message and fix the issue
- You may need to manually intervene if there are conflicts
- In development, you can reset the database with `manage_db reset` if needed

### Data Seeding Issues
- Check that all required environment variables are set
- Verify that the database tables exist before seeding
- Look for error messages in the console output

## Security Considerations

- Never commit sensitive information like database passwords to version control
- Use environment variables for configuration
- Restrict database access to trusted IP addresses
- Regularly back up your database
- Use strong passwords for database users
