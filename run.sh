#/bin/bash

chrome http://127.0.0.1:5000/ & >/dev/null
./run-redis.sh

source env/bin/activate
env/bin/celery worker -A app.celery --loglevel=info &

env/bin/python app.py
