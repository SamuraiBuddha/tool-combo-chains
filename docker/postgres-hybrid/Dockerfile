# PostgreSQL 16 with pgvector and Apache AGE
FROM postgres:16

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-16 \
    curl \
    ca-certificates \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector
RUN cd /tmp && \
    git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd / && \
    rm -rf /tmp/pgvector

# Install Apache AGE
RUN cd /tmp && \
    git clone --branch release/PG16/1.5.0 https://github.com/apache/age.git && \
    cd age && \
    make && \
    make install && \
    cd / && \
    rm -rf /tmp/age

# Add configuration for shared_preload_libraries
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample

# Copy initialization scripts
COPY docker/postgres-hybrid/scripts/init-db.sql /docker-entrypoint-initdb.d/

# Set the default database and user
ENV POSTGRES_DB=cognitive
ENV POSTGRES_USER=cognitive
