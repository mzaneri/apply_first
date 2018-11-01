import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from jobchecker import LazyJobChecker
from create_db import create_db
from scrape import scrape

create_db()

app = Flask(__name__)

cron = BackgroundScheduler(daemon=True)
cron.add_job(func=scrape, trigger='interval', seconds=30)
cron.start()

atexit.register(lambda: cron.shutdown())

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)