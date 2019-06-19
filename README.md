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
1. Download install and setup [docker-cli](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) based on your machine.
2. Clone or download the project to your local machine

## Running the Data Resource API
This project uses docker and docker-compose for building and running the data-resource-api.

### Build Docker Image
First, you will need to build the docker image using the command:
```bash
cd path/to/data_resource_api
mkdir migrations/versions
docker build -t brighthive/data-resource-api:1.0.0-alpha .
```
### Running Docker Container
Now that you have the image of the data resource api built, now you can stand up the data resource api containers using docker-compose:
```bash
cd path/to/data_resource_api
docker-compose up
```

If you need to run the data resource api in the background as a daemon process, use the following command:
```bash
cd path/to/data_resource_api
docker-compose up -d
```
### Stopping the Docker Containers
To stop the container running in the foreground(without the -d argument), you will need to send a SIGKILL signal using CTRL+C. Then follow up with:
```bash
docker-compose down
```

