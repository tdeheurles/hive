FROM       __OS__
MAINTAINER __MAINTAINER__

COPY install.sh /tmp/install.sh
RUN  cd /tmp && ./install.sh

COPY       app /opt
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
