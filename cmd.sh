#!/bin/bash

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    gunicorn -b 0.0.0.0:5000 wsgi:app --reload
else
    gunicorn -b 0.0.0.0 wsgi:app
fi