FROM python:3.7.3-slim
WORKDIR /data-resource
ADD migrations migrations
ADD schema schema
ADD alembic.ini alembic.ini
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
ADD wsgi.py wsgi.py
RUN apt-get update && apt-get install -y python3-dev build-essential &&\ 
    pip install --upgrade pipenv && pipenv install --system &&\
    apt-get remove -y python3-dev build-essential
ADD cmd.sh cmd.sh
RUN chmod a+x cmd.sh
ADD data_resource_api data_resource_api
ENTRYPOINT [ "/data-resource/cmd.sh" ]