FROM ubuntu:16.04

RUN apt-get clean
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip
RUN pip3 install pipenv

ADD .. /bosslet

RUN export LC_ALL=C.UTF-8 ; export LANG=C.UTF-8 ; \
    cd /bosslet && pipenv install --system

EXPOSE 5000

ENTRYPOINT cd /bosslet && \
    python3 /bosslet/run.py
