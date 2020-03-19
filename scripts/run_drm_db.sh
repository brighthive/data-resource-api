#!/bin/bash

docker build -t brighthive/data-resource-api:1.1.0-alpha . && docker system prune -f && docker-compose up data-resource-api postgres