#!/bin/bash

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    python data_model_manager_runner.py &
    DATA_MODEL_MANAGER_PID=$!
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app --reload
    trap "kill -9 $DATA_MODEL_MANAGER_PID" EXIT
else
    MODE=$@
    if [ "$MODE" == "--data-model-manager" ]; then
        python data_model_manager_runner.py
    else
        if [ -z "$GUNICORN_WORKERS" ]; then
            GUNICORN_WORKERS=4
        fi
        gunicorn -b 0.0.0.0 -w $GUNICORN_WORKERS wsgi:app
    fi
fi