import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from jobchecker import LazyJobChecker
from create_db import create_db
from job import job

create_db()

app = Flask(__name__)

cron = BackgroundScheduler(daemon=True)
cron.add_job(func=job, trigger='interval', seconds=60)
cron.start()

atexit.register(lambda: cron.shutdown())

if __name__ == "__main__":
    app.run(debug=True)