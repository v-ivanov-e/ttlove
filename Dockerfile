FROM python:3.11.0a5-bullseye

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ARG SLACK_TOKEN
ENV SLACK_TOKEN=$SLACK_TOKEN

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "wsgi:app"]
EXPOSE 80
