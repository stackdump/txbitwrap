FROM python:2.7.13

WORKDIR /opt/txbitwrap
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN pip install .

VOLUME ["/opt/bitwrap", "/repo"]

ENV PNML_PATH=/opt/txbitwrap/schemata

EXPOSE 8080

ENTRYPOINT ["/opt/txbitwrap/entry.sh"]
