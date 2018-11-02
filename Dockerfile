FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev libffi-dev unzip python-selenium wget chromium\
  --no-install-recommends 

WORKDIR /usr/app

COPY requirements.txt requirements.txt
RUN python -m venv .
RUN bin/pip install --upgrade pip
RUN bin/pip install -r requirements.txt

RUN wget https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/bin
RUN chmod +x /usr/bin/chromedriver

COPY run.sh app.py create_db.py jobchecker.py scrape.py  companies.txt ./
RUN chmod +x run.sh

ENV SENTRY_KEY ****CHANGE_ME****

EXPOSE 5000
ENTRYPOINT ["./run.sh"]
