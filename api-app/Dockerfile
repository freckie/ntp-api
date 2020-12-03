FROM python:3.8

EXPOSE 8000

ADD . /www
WORKDIR /www

RUN pip3 install -r requirements.txt && pip3 install uwsgi

CMD ["uwsgi", "--ini", "uwsgi.ini"]