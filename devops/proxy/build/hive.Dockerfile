FROM <% local_cluster_proxy.base %>
MAINTAINER <% maintainer %>

COPY http.nginx.conf /tmp/http.nginx.conf
COPY ws.nginx.conf /tmp/ws.nginx.conf
COPY start.sh /start.sh


RUN chmod 755 start.sh
CMD ["/start.sh"]
