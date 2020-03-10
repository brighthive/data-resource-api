#!/bin/bash

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    python data_model_manager_runner.py &
    DATA_MODEL_MANAGER_PID=$!
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app --reload --worker-class gevent
    trap "kill -9 $DATA_MODEL_MANAGER_PID" EXIT
else
    MODE=$@
    if [ "$MODE" == "--upgrade-104-to-110" ]; then
        python 104_to_110.py
        exit 1
    fi
    if [ "$MODE" == "--data-model-manager" ]; then
        python data_model_manager_runner.py
    else
        if [ -z "$GUNICORN_WORKERS" ]; then
            GUNICORN_WORKERS=4
        fi
        gunicorn -b 0.0.0.0 -w $GUNICORN_WORKERS wsgi:app --worker-class gevent
    fi
fi