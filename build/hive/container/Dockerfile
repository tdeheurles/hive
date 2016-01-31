FROM       ubuntu:15.10
MAINTAINER thibault deheurles <tdeheurles@gmail.com>

COPY       install.sh /tmp/install.sh
RUN        cd /tmp && ./install.sh

COPY       main.py /opt/main.py
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
CMD        ["-h"]
