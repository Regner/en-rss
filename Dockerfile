

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

ENV GOOGLE_APPLICATION_CREDENTIALS "path-to-credentials.json"
ENV GCLOUD_DATASET_ID "your gce project"
ENV SLEEP_TIME "120"
ENV EN_TOPIC_SETTINGS "http://en-topic-settings/external"
ENV NOTIFICATION_TOPIC "send_notification"

ADD en_rss.py /en_rss/
ADD requirements.txt /en_rss/

WORKDIR /en_rss/

RUN apt-get update -qq \
&& apt-get upgrade -y -qq \
&& apt-get install -y -qq python-dev python-pip \
&& apt-get autoremove -y \
&& apt-get clean autoclean \
&& pip install -qU pip \
&& pip install -r requirements.txt

CMD python /en_rss/en_rss.py
