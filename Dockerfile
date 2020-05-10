FROM python:3.7.5-slim

RUN apt-get update -q \
   && apt-get install --no-install-recommends -qy \
       git \
   && rm -rf /var/lib/apt/lists/*

COPY [ "requirements.txt", "/vectorcloud/" ]

WORKDIR /vectorcloud

RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY [ ".", "/vectorcloud/" ]
ENV FLASK_DEBUG=1
ENV FLASK_APP=./run.py
ENV VC_DOCKER_CONTAINER="true"
EXPOSE 5000
VOLUME /vectorcloud/vectorcloud/user_data

ENTRYPOINT [ "flask", "run" ]
