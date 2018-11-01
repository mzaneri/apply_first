FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev libffi-dev --no-install-recommends python-selenium chromium-chromedriver

WORKDIR /usr/app

COPY requirements.txt requirements.txt
RUN python -m venv .
RUN bin/pip install -r requirements
#RUN bin/pip install --upgrade sentry-sdk[flask]==0.5.2

RUN wget https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/bin
RUN chmod +x /usr/bin/chromedriver

COPY run.py jobchecker.py job.py run.py create_db.py run.sh companies.txt./
RUN chmod +x run.sh

ENV SENTRY_KEY ****your_sentry_api_project_key****

EXPOSE 5000

ENTRYPOINT ["./run.sh"]
