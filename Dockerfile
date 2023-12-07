FROM python:3.10-alpine

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

RUN touch -c /app/database.db

EXPOSE 5000

ENTRYPOINT ["python"]

CMD ["app.py"]