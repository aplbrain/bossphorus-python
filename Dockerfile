FROM ubuntu:18.04
LABEL maintainer="Jordan Matelsky <jordan.matelsky@jhuapl.edu>"

RUN apt-get clean
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip

ADD . /bossphorus
RUN pip3 install poetry
RUN cd /bossphorus && poetry install


ENTRYPOINT python3 /bossphorus/bossphorus/__main__.py
