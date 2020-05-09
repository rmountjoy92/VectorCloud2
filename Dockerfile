FROM python:3.7.5-slim

RUN apt-get update -q \
   && apt-get install --no-install-recommends -qy \
       git \
   && rm -rf /var/lib/apt/lists/*

RUN useradd -rm -d /home/vc_user -s /bin/bash -g root -G sudo -u 1000 vc_user

USER vc_user

COPY [ "requirements.txt", "/vectorcloud/" ]

WORKDIR /vectorcloud

RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY [ ".", "/vectorcloud/" ]

ENV PRODUCTION=true
EXPOSE 5000
VOLUME /vectorcloud/vectorcloud/user_data
CMD gunicorn --worker-class eventlet --bind 0.0.0.0:5000 -w 1 run:app
