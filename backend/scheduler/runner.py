"""APScheduler job runner."""
from apscheduler.schedulers.background import BackgroundScheduler
from backend.scheduler.jobs import JOBS

class JobRunner:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def register(self, job_id: str, func, minutes: int):
        self.scheduler.add_job(func, "interval", minutes=minutes, id=job_id)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
