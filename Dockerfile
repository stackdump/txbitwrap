FROM python:2.7.13

WORKDIR /opt/txbitwrap
COPY . .
RUN pip -r requirements.txt
RUN pip install .

VOLUME ["/opt/bitwrap", "/repo"]

ENV SCHEMA_PATH=/opt/txbitwrap/schemata

EXPOSE 8080

ENTRYPOINT ["/opt/txbitwrap/entry.sh"]

