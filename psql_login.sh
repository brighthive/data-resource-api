#!/bin/bash

PSQL_USER=test_user
PSQL_DB=data_resource_dev

docker exec -it docker_postgres_1 psql -U $PSQL_USER -d $PSQL_DB