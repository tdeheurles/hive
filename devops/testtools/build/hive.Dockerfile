FROM            <% os %>
MAINTAINER 	    <% maintainer %>

ENV             JQ_VERSION 1.5

WORKDIR         /root
RUN             apt-get update && apt-get install curl -y
RUN             curl --silent -L -o jq https://github.com/stedolan/jq/releases/download/jq-${JQ_VERSION}/jq-linux64
RUN             chmod 755 jq

RUN             mkdir /test
WORKDIR         /test

ENV             PATH  $PATH:/root

CMD             curl
