FROM       <% image.os %>
MAINTAINER <% maintainer %>

COPY install.sh /tmp/install.sh
RUN  cd /tmp && ./install.sh

COPY       app /opt
WORKDIR    /opt
ENTRYPOINT ["python", "main.py"]
