FROM python:3.7.5-slim

RUN apt-get update -q \
   && apt-get install --no-install-recommends -qy \
       git \
   && rm -rf /var/lib/apt/lists/*

COPY [ "requirements.txt", "/vectorcloud/" ]

WORKDIR /vectorcloud

RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY [ ".", "/vectorcloud/" ]

ENV PRODUCTION=true
EXPOSE 5000
VOLUME /vectorcloud/vectorcloud/user_data
CMD gunicorn -t 300 --worker-class eventlet --bind 0.0.0.0:5000 -w 1 run:app
