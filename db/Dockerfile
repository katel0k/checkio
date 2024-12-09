FROM postgres

ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin
ENV POSTGRES_DATABASE=checkers_db
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST_AUTH_METHOD=trust

WORKDIR /

EXPOSE 5432

RUN apt-get update 
RUN apt-get install python3 postgresql-plpython3-17 -y

COPY db_ddl.sql /docker-entrypoint-initdb.d/
COPY db_rework.sql /docker-entrypoint-initdb.d/
COPY game_logic.py /
