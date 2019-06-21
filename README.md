# Data Resource API

An elegant, opinionated framework for deploying BrightHive Data Resources with zero coding.

## What is a Data Resource

[BrightHive](https://brighthive.io) is in the business of building **Data Trusts**, which are *legal, technical, and governance frameworks that enable networks of organizations to securely and responsibly share and collaborate with data, generating new insights and increasing their combined impact.*

**Data Resources** are a core element of Data Trusts and may be loosely defined as *data that is owned by or stewarded over by members of Data Trusts.*

From the technical perspective, a BrightHive Data Resource is an entity comprised of the following elements:

- **Data Model** - The data model consists of one or more database tables and associated Object Relational Mapping (ORM) objects for communicating with these tables.
- **RESTful API** - Data managed by Data Resources are accessed via RESTful API endpoints. These endpoints support standard operations (i.e **GET**, **POST**, **PUT**, **PATCH**, **DELETE**).
- **Data Resource Schemas** - Data Resource Schemas are JSON documents that define the data model, API endpoints, and security constraints placed on the specific Data Resource. These schemas are what allow for new Data Resources to be created without new code being written.

## Get started

Spinning up a fresh, out-of-the-box Data Resource API requires minimal setup. Follow these steps:


**1. Download install [docker-cli](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) based on your machine and preferences (e.g., you may chose to run `docker-compose` in a virtualenv.)**

**2. Clone or download the project to your local machine**

```bash
git clone https://github.com/brighthive/data-resource-api.git
```

**3. Build the Docker image with specified tag**

```bash
# run this command in the root of the data-resource-api repo
docker build -t brighthive/data-resource-api:1.0.0-alpha .
```

**4. Launch Docker containers**

```bash
# run this command in the root of the data-resource-api repo
docker-compose up
```

Alternatively, you can run the data resource api in the background:
```bash
docker-compose up -d
```

Visit `http://0.0.0.0:8000/programs` to test the API URL (though expect an "Access Denied" message).

Note! The default `docker-compose.yml` launches three containers: postgres_1, data-model-manager_1, and data-resource-api_1. Expect the postgres container to raise an error, at first, something like: `ERROR:  relation "checksums" does not exist at character 171`. This occurs temporarily, as Docker spins up the data-model-manager_1, the service that creates and runs migrations. 

## Data and endpoints 

The Data Resource API auto-magically instantiates data stores and corresponding endpoints without any coding. 

Each JSON file in the `schema` directory delineates a resource, namely: its RESTful paths ("api"), and its data model ("datastore"). Create a new resource by adding another JSON file to the `schema` directory. (Visit `schema/data-resource-api` for an example JSON file.)

### Enable or disable methods

A resource JSON blob should define RESTful methods. These can be enabled or disabled.

```JSON
{
  "api": {
    "resource": "name_of_endpoint",
    "methods": [
      {
        "get": {
          "enabled": true, # enable the method
          "secured": true,
          "grants": ["get:users"]
        },
        "post": {
          "enabled": false, # disable the method
          "secured": true,
          "grants": ["get:users"]
        },
...
```

### Toggle authentication

The Data Resource API makes use of the BrightHive authlib for adding authentication to endpoints. Authentication can be toggle on or off – on a per method basis. 

```JSON
{
  "api": {
    "resource": "name_of_endpoint",
    "methods": [
      {
        "get": {
          "enabled": true,
          "secured": false, # do not require authentication
          "grants": ["get:users"]
        },
        "post": {
          "enabled": false,
          "secured": true, # require authentication
          "grants": ["get:users"]
        },
...
```