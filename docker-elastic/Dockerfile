FROM elasticsearch:latest
MAINTAINER bojieli@gmail.com

# install logstash
RUN wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN echo "deb http://packages.elastic.co/logstash/2.1/debian stable main" | tee -a /etc/apt/sources.list
RUN apt-get update && apt-get install -y logstash
COPY docker-entrypoint.sh /docker-entrypoint.sh
