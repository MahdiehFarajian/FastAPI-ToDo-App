#!/bin/sh

echo 'migrating database changes'
alembic upgrade heads

echo 'compiling languages locales'
pybabel compile -d locales

echo 'initiating server'
fastapi run --host 0.0.0.0 --port 8000