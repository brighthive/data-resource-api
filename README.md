# Data Resource API

An elegant, opinionated framework for deploying BrightHive Data Resources with zero coding.

## What is a Data Resource

[BrightHive](https://brighthive.io) is in the business of building **Data Trusts**, which are *legal, technical, and governance frameworks that enable networks of organizations to securely and responsibly share and collaborate with data, generating new insights and increasing their combined impact.*

**Data Resources** are a core element of Data Trusts and may be loosely defined as *data that is owned by or stewarded over by members of Data Trusts.*

From the technical perspective, a BrightHive Data Resource is an entity comprised of the following elements:

- **Data Model** - The data model consists of one or more database tables and associated Object Relational Mapping (ORM) objects for communicating with these tables.
- **RESTful API** - Data managed by Data Resources are accessed via RESTful API endpoints. These endpoints support standard operations (i.e **GET**, **POST**, **PUT**, **PATCH**, **DELETE**).
- **Data Resource Schemas** - Data Resource Schemas are JSON documents that define the data model, API endpoints, and security constraints placed on the specific Data Resource. These schemas are what allow for new Data Resources to be created without new code being written.


## Installation
1. Download install [docker-cli](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) based on your machine.
2. Clone or download the project to your local machine

## Basic Usage
The project uses docker and docker compose to build and stand up the api end points by providing Dockerfile and docker compose yaml.

### Build Docker Image
You will need to build the docker image using the following tag:
```bash
cd path/to/data_resource_api
docker build -t brighthive/data-resource-api:1.0.0-alpha .
```
### Running Docker Container
To run the data resource api, you will need to use docker compose since we will need to use a postgres docker container:
```bash
cd path/to/data_resource_api
docker-compose up
```

To run the data resource api in the background as a daemon process:
```bash
cd path/to/data_resource_api
docker-compose up -d
```
### Stopping the Docker Containers
To stop the container running in the foreground(without the -d argument), you will need to send a SIGKILL signal using CTRL+C. Then follow with:
```bash
docker-compose down
```

### Using the data resource api and data model manager to create new endpoints
The data resource api framework was built for extensibility and provides the ability to create data resource endpoints and data stores without any coding.

To create a new end point and data store, you will first need to create a JSON configuration file that defines the resource endpoint and the data store schema. 
The config file should have the following structure:
```json

{
  "api": {
    "resource": "credentials",
    "methods": [
      {
        "get": {
          "enabled": true,
          "secured": false,
          "grants": ["get:users"]
        },
        "post": {
          "enabled": true,
          "secured": false,
          "grants": []
        },
        "put": {
          "enabled": true,
          "secured": true,
          "grants": []
        },
        "patch": {
          "enabled": true,
          "secured": true,
          "grants": []
        },
        "delete": {
          "enabled": true,
          "secured": true,
          "grants": []
        }
      }
    ]
  },
  "datastore": {
    "tablename": "credentials",
    "restricted_fields": [],
    "schema": {
      "fields": [
        {
          "name": "id", 
          "title": "Credential ID",
          "type": "integer",
          "description": "Credential's unique identifier",
          "required": false
        },
        {
          "name": "credential_name",
          "title": "Credential Name",
          "type": "string",
          "description": "Credential's Name",
          "required": true
        }
      ],
      "primaryKey": "id" # Name of the field that will be used as a primary key
    }
  }
}  
}
```
