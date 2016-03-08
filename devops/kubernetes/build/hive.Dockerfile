FROM <% kubernetes.base %>:<% cli.kubernetes_version %>
MAINTAINER <% maintainer %>

COPY update.sh /update.sh
RUN /update.sh

COPY start.sh /start.sh

CMD ["/start.sh", "--port", "8080"]
