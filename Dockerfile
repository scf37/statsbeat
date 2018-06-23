FROM scf37/base:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install requests pyyaml


COPY statsbeat.py /opt/statsbeat.py
COPY app.sh /opt/app.sh
COPY statsbeat.yml /opt/statsbeat.yml
COPY checks /opt/checks
COPY plugins /opt/plugins

ENTRYPOINT /opt/app.sh