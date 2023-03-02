FROM python:3.8

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

EXPOSE 80

CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:80", "main:app"]