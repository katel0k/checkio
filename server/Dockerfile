FROM python:3.11-alpine

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000
ENV FLASK_APP=server
ENV FLASK_RUN_HOST=0.0.0.0
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432
ENV DATABASE_USER=admin
ENV DATABASE_PASSWORD=admin
ENV STATIC_FOLDER=../client
ENV TEMPLATE_FOLDER=../client/templates
ENV SECRET_KEY=SHAURMA
COPY . ./server

CMD ["flask", "run", "--debug"]
