FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y python3-dev python3-pip
RUN pip install pipenv

ADD . /bosslet

RUN cd /bosslet && pipenv install

EXPOSE 5000

ENTRYPOINT ["python3" "/bosslet/run.py"]
