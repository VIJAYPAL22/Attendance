from app import create_app
from app.scheduler import start_scheduler

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print("Starting background scheduler...")
        start_scheduler()
        # Keep the process alive
        import time
        while True:
            time.sleep(60)
