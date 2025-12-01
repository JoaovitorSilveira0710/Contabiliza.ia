import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run")

def main():
    try:
        logger.info("Starting Contabiliza.IA (Django)...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        django_backend_dir = os.path.join(current_dir, "django_backend")
        
        if not os.path.exists(django_backend_dir):
            logger.error("Directory 'django_backend' not found!")
            logger.info("Run this script from the project root")
            return
        
        logger.info(f"Project directory: {current_dir}")
        
        # Apply migrations
        logger.info("Applying database migrations...")
        subprocess.run(
            [sys.executable, "manage.py", "makemigrations"],
            cwd=django_backend_dir,
            check=True
        )
        subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            cwd=django_backend_dir,
            check=True
        )
        
        # Start Django server
        logger.info("Starting Django server...")
        logger.info("API available at: http://localhost:8000/api/")
        logger.info("Admin panel at: http://localhost:8000/admin/")
        
        subprocess.run(
            [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
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