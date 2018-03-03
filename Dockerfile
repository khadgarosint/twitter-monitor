FROM python:3.6-alpine3.6

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python twitter-monitor.py

