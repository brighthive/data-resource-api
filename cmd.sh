#!/bin/bash

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app --reload
else
    gunicorn -b -w 4 0.0.0.0 wsgi:app
fi
