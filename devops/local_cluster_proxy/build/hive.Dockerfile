FROM <% local_cluster_proxy.base %>
MAINTAINER <% maintainer %>

COPY nginx.conf /etc/nginx/nginx.conf

