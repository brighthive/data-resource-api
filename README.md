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


**1. Download install [docker-cli](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) based on your machine and preferences (e.g., you may chose to run `docker-compose` in a virtualenv).**

**2. Clone or download the project to your local machine**

```bash
git clone git@github.com:brighthive/data-resource-api.git
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

*Note!* The default `docker-compose.yml` launches three containers: `postgres`, `data-model-manager`, and `data-resource-api`. Expect the postgres container to raise an error, at first, something like: `ERROR:  relation "checksums" does not exist at character 171`. This occurs temporarily, as Docker spins up the `data-model-manager` (i.e., the service that creates and runs migrations). Once the model manager has done its business, the `data-resource-manager` can ease-fully listen for incoming schema files. A successful launch should continuously log the following happy messages:

```
data-resource-api_1   | 2019-06-21 21:31:21,392 - data-resource-manager - INFO - Data Resource Manager Running...
data-resource-api_1   | 2019-06-21 21:31:21,393 - data-resource-manager - INFO - Checking data resources...
data-resource-api_1   | 2019-06-21 21:31:21,413 - data-resource-manager - INFO - Completed check of data resources
data-resource-api_1   | 2019-06-21 21:31:21,414 - data-resource-manager - INFO - Data Resource Manager Sleeping for 60 seconds...
```

## Data and endpoints 

The Data Resource API auto-magically instantiates data stores and corresponding endpoints without any coding. 

Each JSON file in the `schema` directory delineates a resource, namely: its RESTful paths ("api"), and its data model ("datastore"). Create a new resource by adding another JSON file to the `schema` directory. (Visit `schema/data-resource-api` for an example JSON file.)

### Enable or disable methods

A resource JSON blob should define RESTful methods. These can be enabled or disabled.

```
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

The Data Resource API makes use of [the BrightHive authlib](https://github.com/brighthive/authlib) for adding authentication to endpoints. Authentication can be toggle on or off – on a per method basis. 

```
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

### Define the Table Schema

The Data Resource API utilizes [the Table Schema from fictionless data](https://frictionlessdata.io/specs/table-schema/). The Table Schema is represented by a "descriptor", or a JSON object with particular attributes. In a Data Resource schema, the descriptor occupies the value of "datastore" >> "schema" (see `schema/programs.json` for an example). A schema can have up to four properties, among them: `primaryKey`, `foreignKeys`, and `fields`. 

The `fields` must be an array of JSON objects, and each object must define a field on the data model. A field definition should include, at minimum, a `name`, `type` (defaults to String), and `required` (defaults to `false`). 

Frictionless data and, correspondingly, the Data Resource API can be particular about what goes inside a field descriptor. `TABLESCHEMA_TO_SQLALCHEMY_TYPES` defines the available types in the frictionless schema and the corresponding types in sqlalchemy. Stick to these types, or you can anticipate unexpected behavior in your API! (See `data-resource-api/data_resource_api/factories/table_schema_types.py` for more context.)

```python
TABLESCHEMA_TO_SQLALCHEMY_TYPES = {
    'string': String,
    'number': Float,
    'integer': Integer,
    'boolean': Boolean,
    'object': String,
    'array': String,
    'date': Date,
    'time': DateTime,
    'datetime': DateTime,
    'year': Integer,
    'yearmonth': Integer,
    'duration': Integer,
    'geopoint': String,
    'geojson': String,
    'any': String
}
```

### Add foreign keys

Creating a foreign key two involves making two additions to the JSON blob. 

First, add the foreign key as a field in the `schema`:

```
  "datastore": {
    "tablename": "programs",
    "restricted_fields": [],
    "schema": {
      "fields": [
        {
          "name": "location_id",
          "title": "Provider ID",
          "type": "integer",
          "description": "Foreign key for provider",
          "required": false
        },
...
```

Second, define the foreign key in the `foreignKeys` array:

```
"datastore": {
  "tablename": "programs",
  "restricted_fields": [],
  "schema": {  
    "fields": [ 
      // Descriptor for location_id field
...

    ],
    "foreignKeys": [
      {
        "fields": ["location_id"],
        "reference": {
          "resource": "locations",
          "fields": ["id"]
        }
      }
    ]
  }
}
```