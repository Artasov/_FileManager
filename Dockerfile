FROM python:3.9

ADD requirements.txt /srv/requirements.txt
COPY entrypoint.sh /srv/entrypoint.sh

RUN apt-get update \
    && apt-get install -yyq netcat

RUN apt-get install -y libpq-dev \
    && python -m pip install --upgrade pip \
    && python -m pip install -r /srv/requirements.txt

COPY . /srv
WORKDIR /srv

RUN echo "Europe/Moscow" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

ENTRYPOINT ["./entrypoint.sh"]

