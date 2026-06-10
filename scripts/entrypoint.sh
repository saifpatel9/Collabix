#!/bin/sh
set -e

python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec "$@"