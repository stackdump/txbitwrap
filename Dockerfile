FROM python:2.7.13

WORKDIR /opt/txbitwrap
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN pip install .

EXPOSE 8080

ENTRYPOINT ["./entry.sh"]
