FROM       <% os %>
MAINTAINER <% maintainer %>

COPY install.sh /tmp/install.sh
RUN  cd /tmp && ./install.sh

RUN touch /hivecontainer

COPY       src /opt
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
