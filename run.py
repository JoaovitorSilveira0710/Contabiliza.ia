import os
import sys
import subprocess
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run")

def main():
    parser = argparse.ArgumentParser(description="Run Contabiliza.IA backend")
    parser.add_argument("--reset", action="store_true", help="Reset SQLite DB (delete and recreate)")
    parser.add_argument("--seed", action="store_true", help="Seed demo clients after migrations")
    parser.add_argument("--port", default="8000", help="Port for Django runserver (default: 8000)")
    args = parser.parse_args()
    try:
        logger.info("Starting Contabiliza.IA (Django)...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        django_backend_dir = os.path.join(current_dir, "django_backend")
        
        if not os.path.exists(django_backend_dir):
            logger.error("Directory 'django_backend' not found!")
            logger.info("Run this script from the project root")
            return
        
        logger.info(f"Project directory: {current_dir}")
        
        # Prefer venv Python if available
        venv_python = os.path.join(current_dir, "venv", "Scripts", "python.exe")
        python_exec = venv_python if os.path.exists(venv_python) else sys.executable
        logger.info(f"Using Python executable: {python_exec}")

        # Optional reset of SQLite DB
        db_path = os.path.join(django_backend_dir, "db.sqlite3")
        if args.reset and os.path.exists(db_path):
            try:
                os.remove(db_path)
                logger.info(f"Removed SQLite DB: {db_path}")
            except Exception as e:
                logger.error(f"Failed to remove DB: {e}")
                sys.exit(1)

        # Apply migrations
        logger.info("Applying database migrations...")
        subprocess.run(
            [python_exec, "manage.py", "makemigrations"],
            cwd=django_backend_dir,
            check=True
        )
        subprocess.run(
            [python_exec, "manage.py", "migrate"],
            cwd=django_backend_dir,
            check=True
        )

        # Optional seeding
        if args.seed:
            logger.info("Seeding demo clients...")
            try:
                subprocess.run(
                    [python_exec, "manage.py", "seed_clients", "--count", "12", "--created-by-email", "admin@contabiliza.ia"],
                    cwd=django_backend_dir,
                    check=False
                )
            except Exception as e:
                logger.warning(f"Seeding failed or partially completed: {e}")
        
        # Start Django server
        logger.info("Starting Django server...")
        logger.info(f"API available at: http://localhost:{args.port}/api/")
        logger.info(f"Admin panel at: http://localhost:{args.port}/admin/")

        subprocess.run(
            [python_exec, "manage.py", "runserver", f"0.0.0.0:{args.port}"],
            cwd=django_backend_dir,
            check=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()