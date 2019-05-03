#!/bin/bash

python data_model_manager_runner.py &
DATA_MODEL_MANAGER_PID=$!

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app --reload
else
    gunicorn -b 0.0.0.0 -w 4 wsgi:app
fi

trap "kill -9 $DATA_MODEL_MANAGER_PID" EXIT