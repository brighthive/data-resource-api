FROM python:3.7.3-slim
WORKDIR /data-resource
RUN apt-get update && apt-get install -y python3-dev build-essential &&\ 
    pip install --upgrade pipenv
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pipenv install --system &&\
    apt-get remove -y python3-dev build-essential
ADD wsgi.py wsgi.py
ADD alembic.ini alembic.ini
ADD data_model_manager_runner.py data_model_manager_runner.py
ADD cmd.sh cmd.sh
RUN chmod a+x cmd.sh
ADD migrations migrations
ADD schema schema
ADD data_resource_api data_resource_api
ENTRYPOINT [ "/data-resource/cmd.sh" ]