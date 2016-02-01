FROM       __OS__
MAINTAINER __MAINTAINER__

RUN apt-get update
RUN apt-get install python python-pip -y
RUN pip install pyyaml

COPY       app /opt
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
