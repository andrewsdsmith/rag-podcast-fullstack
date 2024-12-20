#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Seed the DB using sql dump
# Reference db container by hostname. Include password in env variable

# Export the password so that it can be used by the psql command
export PGPASSWORD="${POSTGRES_PASSWORD}"

# Check if there is any data in the podcast_segment_summaries table 
# if not seed it
if psql -h "${POSTGRES_SERVER}" -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "select count(*) from podcast_segment_summaries;" | grep -q "0"; then
    psql -h "${POSTGRES_SERVER}" -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -a -f app/sql/seed.sql
fi

# Run the FastAPI server
exec "$@"
