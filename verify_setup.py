import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pkg_resources

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{'='*60}")
    print(f"{text.upper()}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(msg: str) -> None:
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg: str, solution: str = "") -> None:
    """Print an error message with an optional solution."""
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")
    if solution:
        print(f"   {Colors.OKBLUE}→ {solution}{Colors.ENDC}")

def print_warning(msg: str, suggestion: str = "") -> None:
    """Print a warning message with optional suggestion."""
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")
    if suggestion:
        print(f"{Colors.WARNING}💡 {suggestion}{Colors.ENDC}")

def check_python_version() -> bool:
    """Check if Python version is 3.9 or higher."""
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print_success(f"Python {'.'.join(map(str, current_version))} is compatible")
        return True
    else:
        print_error(
            f"Python {'.'.join(map(str, current_version))} is not supported",
            f"Please install Python 3.9 or higher"
        )
        return False

def check_packages() -> Dict[str, bool]:
    """Check if all required packages are installed."""
    print_header("Checking Required Packages")
    
    required = {
        'fastapi': '0.104.1',
        'uvicorn': '0.24.0',
        'python-dotenv': '1.0.0',
        'pydantic': '2.8.0',
        'pydantic-settings': '2.10.1',
        'python-jose': '3.3.0',
        'passlib': '1.7.4',
        'python-multipart': '0.0.6',
        'aiofiles': '23.2.1',
        'sqlalchemy': '2.0.43',
        'alembic': '1.12.1',
        'psycopg2-binary': '2.9.10'
    }
    
    results = {}
    for package, version in required.items():
        try:
            pkg = pkg_resources.get_distribution(package)
            if pkg_resources.parse_version(pkg.version) >= pkg_resources.parse_version(version):
                print_success(f"{package} >= {version} (found {pkg.version})")
                results[package] = True
            else:
                print_error(
                    f"{package} version {pkg.version} is below required {version}",
                    f"Run: pip install --upgrade {package}>={version}"
                )
                results[package] = False
        except pkg_resources.DistributionNotFound:
            print_error(
                f"{package} is not installed",
                f"Run: pip install {package}>={version}"
            )
            results[package] = False
    
    return results

def check_directory_structure() -> Dict[str, bool]:
    """Check if required directories exist."""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        'app',
        'app/api',
        'app/api/v1',
        'app/core',
        'app/models',
        'app/schemas',
        'tests',
        'docs',
        'logs',
        'data',
        'static',
        'templates',
        'uploads'
    ]
    
    results = {}
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_success(f"Directory exists: {dir_path}")
            results[dir_path] = True
        else:
            print_warning(f"Directory missing: {dir_path}")
            results[dir_path] = False
    
    return results

def check_environment_variables() -> bool:
    """Check if required environment variables are set."""
    print_header("Checking Environment Variables")
    
    required_vars = [
        'APP_ENV',
        'SECRET_KEY',
        'ALGORITHM',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'DATABASE_URL'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    all_present = True
    for var in required_vars:
        if os.getenv(var):
            print_success(f"{var} is set")
        else:
            print_warning(f"{var} is not set")
            all_present = False
    
    return all_present

def check_database_connection() -> bool:
    """Check if database connection can be established."""
    print_header("Checking Database Connection")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.exc import SQLAlchemyError
        
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
        if 'sqlite' in db_url:
            db_url = 'sqlite:///./test.db'
        
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                print_success("Successfully connected to the database")
                return True
        except SQLAlchemyError as e:
            print_error(
                f"Failed to connect to database: {str(e)}",
                "Check your DATABASE_URL in .env file"
            )
            return False
            
    except ImportError as e:
        print_error(
            f"Failed to import database dependencies: {str(e)}",
            "Make sure SQLAlchemy is installed: pip install sqlalchemy"
        )
        return False

def check_file_permissions() -> bool:
    """Check if file upload directories have proper permissions."""
    print_header("Checking File Permissions")
    
    upload_dirs = ['data', 'data/uploads']
    all_ok = True
    
    for dir_path in upload_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print_success(f"Created directory: {dir_path}")
            except OSError as e:
                print_error(
                    f"Failed to create directory {dir_path}: {str(e)}",
                    "Check directory permissions or create it manually"
                )
                all_ok = False
                continue
        
        test_file = os.path.join(dir_path, '.test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print_success(f"Write permission OK: {dir_path}")
        except IOError as e:
            print_error(
                f"No write permission in {dir_path}: {str(e)}",
                f"Run: chmod 775 {dir_path} or adjust permissions"
            )
            all_ok = False
    
    return all_ok

def check_ai_libraries() -> Dict[str, bool]:
    """Check if AI libraries can be imported."""
    print_header("Checking AI Libraries")
    
    ai_libs = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scikit-learn': 'sklearn',
        'torch': 'torch',
        'transformers': 'transformers'
    }
    
    results = {}
    for lib_name, import_name in ai_libs.items():
        try:
            importlib.import_module(import_name)
            print_success(f"Successfully imported {lib_name}")
            results[lib_name] = True
        except ImportError:
            print_warning(
                f"Could not import {lib_name}",
                f"Install with: pip install {lib_name}"
            )
            results[lib_name] = False
    
    return results

def check_fastapi_startup() -> bool:
    """Check if FastAPI app can start without errors."""
    print_header("Testing FastAPI Startup")
    
    test_script = """
from fastapi import FastAPI
from fastapi.testclient import TestClient

try:
    from app.main import app
    
    client = TestClient(app)
    
    def test_read_main():
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    test_read_main()
    print("✅ FastAPI test passed!")
except Exception as e:
    print(f"❌ FastAPI test failed: {str(e)}")
    raise
    """
    
    try:
        # Create a temporary test file
        with open('_test_fastapi.py', 'w') as f:
            f.write(test_script)
        
        # Run the test
        result = subprocess.run(
            [sys.executable, '_test_fastapi.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("FastAPI app started successfully")
            return True
        else:
            print_error(
                "Failed to start FastAPI app",
                result.stderr or result.stdout or "Unknown error occurred"
            )
            return False
            
    except Exception as e:
        print_error(f"Error testing FastAPI startup: {str(e)}")
        return False
    finally:
        # Clean up
        if os.path.exists('_test_fastapi.py'):
            os.remove('_test_fastapi.py')

def main():
    """Main function to run all checks."""
    print(f"\n{Colors.HEADER}{'*'*60}")
    print(f"{'*'*5} ScholarIQ Setup Verification Tool {'*'*5}")
    print(f"{'*'*60}{Colors.ENDC}\n")
    
    # Run all checks
    py_ok = check_python_version()
    pkg_results = check_packages()
    dir_results = check_directory_structure()
    env_ok = check_environment_variables()
    db_ok = check_database_connection()
    perm_ok = check_file_permissions()
    ai_results = check_ai_libraries()
    fastapi_ok = check_fastapi_startup()
    
    # Calculate summary
    all_pkgs_ok = all(pkg_results.values())
    all_dirs_ok = all(dir_results.values())
    all_ai_ok = all(ai_results.values()) if ai_results else True
    
    # Print summary
    print_header("Verification Summary")
    
    summary = {
        "Python Version": py_ok,
        "Required Packages": all_pkgs_ok,
        "Directory Structure": all_dirs_ok,
        "Environment Variables": env_ok,
        "Database Connection": db_ok,
        "File Permissions": perm_ok,
        "AI Libraries": all_ai_ok,
        "FastAPI Startup": fastapi_ok
    }
    
    all_ok = all(summary.values())
    
    for check, status in summary.items():
        status_str = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if status else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"{check}: {status_str}")
    
    if all_ok:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All checks passed! Your environment is ready for development.{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Some checks failed. Please review the messages above.{Colors.ENDC}")
        print(f"\n{Colors.OKBLUE}Next steps:")
        if not py_ok:
            print("- Install Python 3.9 or higher")
        if not all_pkgs_ok:
            print("- Install missing packages with: pip install -r requirements.txt")
        if not all_dirs_ok:
            print("- Create missing directories")
        if not env_ok:
            print("- Set up required environment variables in .env file")
        if not db_ok:
            print("- Check your database configuration")
        if not perm_ok:
            print("- Fix file permissions for upload directories")
        if not all_ai_ok:
            print("- Install required AI libraries")
        if not fastapi_ok:
            print("- Check your FastAPI application for errors")
        print(Colors.ENDC)
        return 1

if __name__ == "__main__":
    sys.exit(main())