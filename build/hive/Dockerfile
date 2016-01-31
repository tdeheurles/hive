FROM       __OS__
MAINTAINER __MAINTAINER__

COPY       install.sh /tmp/install.sh
RUN        cd /tmp && ./install.sh

COPY       main.py /opt/main.py
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
CMD        ["-h"]
