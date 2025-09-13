import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import platform
import signal
import time

def run_command(command: str, cwd: str = None, shell: bool = False) -> int:
    """Run a shell command and return the exit code."""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=sys.stdout,
            stderr=subprocess.STDOUT
        )
        return process.wait()
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Error running command: {e}")
        return 1

def open_browser(port: int) -> None:
    """Open the default web browser to the specified port."""
    url = f"http://localhost:{port}/docs"
    print(f"Opening {url} in your default browser...")
    webbrowser.open(url)

def setup_environment() -> bool:
    """Set up the development environment."""
    print("Setting up development environment...")
    
    # Check if running in a virtual environment
    if not hasattr(sys, 'real_prefix') and not sys.prefix != sys.base_prefix:
        print("⚠ Warning: Not running in a virtual environment")
        create_venv = input("Would you like to create one? [y/N]: ").lower() == 'y'
        if create_venv:
            venv_dir = ".venv"
            print(f"Creating virtual environment in {venv_dir}...")
            if run_command([sys.executable, "-m", "venv", venv_dir]) != 0:
                print("Failed to create virtual environment")
                return False
            print("Virtual environment created successfully")
            
            # Activate the virtual environment
            if platform.system() == "Windows":
                activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
                activate_cmd = f'call "{activate_script}" && {sys.executable} -m pip install -r requirements.txt'
                if run_command(activate_cmd, shell=True) != 0:
                    print("Failed to install dependencies")
                    return False
            else:
                activate_script = os.path.join(venv_dir, "bin", "activate")
                activate_cmd = f'source "{activate_script}" && {sys.executable} -m pip install -r requirements.txt'
                if run_command(activate_cmd, shell=True) != 0:
                    print("Failed to install dependencies")
                    return False
        else:
            print("Continuing without virtual environment...")
    
    # Install development dependencies
    print("Installing development dependencies...")
    if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]) != 0:
        print("Failed to install development dependencies")
        return False
    
    return True

def start_development_server(host: str = "0.0.0.0", port: int = 8000) -> int:
    """Start the FastAPI development server."""
    print(f"Starting development server on http://{host}:{port}")
    
    # Set environment variables
    os.environ["APP_ENV"] = "development"
    os.environ["DEBUG"] = "true"
    os.environ["RELOAD"] = "true"
    
    # Build the uvicorn command
    cmd = [
        "uvicorn",
        "app.main:app",
        f"--host={host}",
        f"--port={port}",
        "--reload",
        "--reload-dir=app",
        "--reload-dir=tests"
    ]
    
    try:
        # Open browser after a short delay
        import threading
        threading.Timer(2, open_browser, args=[port]).start()
        
        # Start the server
        return run_command(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1

def main():
    """Main function to start the development server."""
    print("\n=== ScholarIQ Development Server ===\n")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start the ScholarIQ development server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--no-setup', action='store_true', help='Skip environment setup')
    args = parser.parse_args()
    
    # Run setup if not skipped
    if not args.no_setup:
        if not setup_environment():
            print("Setup failed. Exiting.")
            return 1
    
    # Start the development server
    return start_development_server(args.host, args.port)

if __name__ == "__main__":
    sys.exit(main())