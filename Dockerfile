

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

RUN apt-get update -qq
RUN apt-get upgrade -y
RUN apt-get install -y python-dev python-pip
RUN pip install -qU pip

WORKDIR /en_rss/
CMD python /en_rss/en_rss.py
