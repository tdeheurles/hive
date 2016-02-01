FROM       ubuntu:15.10
MAINTAINER thibault deheurles <tdeheurles@gmail.com>

RUN apt-get update
RUN apt-get install python python-pip -y
RUN pip install pyyaml

COPY       app /opt
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
