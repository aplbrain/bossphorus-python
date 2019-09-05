FROM ubuntu:latest

#RUN apt-get clean
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip git

RUN git clone https://github.com/aplbrain/bossphorus.git
WORKDIR bossphorus
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pip3 install numpy blosc h5py intern flask

CMD ["python3", "./local_debug_run.py"]
