FROM python:3.7.5-slim

RUN apt-get update -q \
  && apt-get install --no-install-recommends -qy \
    inetutils-ping \
  && rm -rf /var/lib/apt/lists/*

COPY [ "requirements.txt", "/vectorcloud/" ]

WORKDIR /vectorcloud

RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY [ ".", "/vectorcloud/" ]

ENV PRODUCTION=true
EXPOSE 5000
VOLUME /vectorcloud/vectorcloud/user_data
CMD [ "gunicorn", "--worker-class eventlet", 'w 1', "0.0.0.0:5000", "wsgi:app" ]
