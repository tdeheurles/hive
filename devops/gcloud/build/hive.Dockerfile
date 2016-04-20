FROM       <% os %>
MAINTAINER <% maintainer %>

COPY       install.sh    /opt/install.sh
RUN        /opt/install.sh

ENV        PATH    /root/google-cloud-sdk/bin:$PATH
CMD        /bin/sh
