FROM python:3.8-slim-buster

WORKDIR /back

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

RUN apt-get update && \
    apt-get install -y locales git&& \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

COPY ./requirements.txt /back/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /back

CMD ["gunicorn", "-b", "127.0.0.1:8000", "run:app"]