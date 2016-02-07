

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmailc.om>

RUN apt-get update -qq
RUN apt-get upgrade -y
RUN apt-get install -y python-dev python-pip
RUN pip install -qU pip
RUN virtualenv /venv
RUN /venv/bin/pip install -U gcloud
RUN apt-get autoremove -y && apt-get clean autoclean

ADD en_rss.py /en_rss/

RUN groupadd -r en_rss \
&& useradd -r -g en_rss -d /venv -s /usr/sbin/nologin -c "en_rss" en_rss \
&& chown -R en_rss:en_rss /venv /en_rss
USER en_rss

WORKDIR /en_rss/
CMD /venv/bin/python /en_rss/en_rss.py
