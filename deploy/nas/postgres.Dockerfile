FROM postgres:16
ARG SCHEMA_PATH
COPY ${SCHEMA_PATH} /docker-entrypoint-initdb.d/01-schema.sql
