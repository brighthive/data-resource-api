# Data Resource API

An elegant, opinionated framework for deploying BrightHive Data Resources with zero coding.

## The "Data Resource" and its related elements

[BrightHive](https://brighthive.io) is in the business of building **Data Trusts**, which are *legal, technical, and governance frameworks that enable networks of organizations to securely and responsibly share and collaborate with data, generating new insights and increasing their combined impact.*

**Data Resources** are a core element of Data Trusts and may be loosely defined as *data that is owned by or stewarded over by members of Data Trusts.*

From the technical perspective, a BrightHive Data Resource is an entity comprised of the following elements:

- **Data Model** - The data model consists of one or more database tables and associated Object Relational Mapping (ORM) objects for communicating with these tables.
- **RESTful API** - Data managed by Data Resources are accessed via RESTful API endpoints. These endpoints support standard operations (i.e. **GET**, **POST**, **PUT**, **PATCH**, **DELETE**).
- **Data Resource Schemas** - Data Resource Schemas are JSON documents that define the data model, API endpoints, and security constraints placed on the specific Data Resource. These schemas are what allow for new Data Resources to be created without new code being written.

## Get started

Spinning up a fresh, out-of-the-box Data Resource API requires minimal setup. Follow these steps:


**1. Download install [docker-cli](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) based on your machine and preferences (e.g., you may choose to run `docker-compose` in a virtualenv).**

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

## Customize your JSON schema 

The Data Resource API auto-magically instantiates data stores and corresponding endpoints without any coding. 

Each JSON file in the `schema` directory delineates a resource, namely: its RESTful paths ("api"), and its data model ("datastore"). Create a new resource by adding another JSON file to the `schema` directory. (Visit the `schema` directory for example JSON files.) 

### Enable or disable methods

A resource JSON blob defines RESTful methods. These can be enabled or disabled.

```JavaScript
{
  "api": {
    "resource": "name_of_endpoint",
    "methods": [
      {
        "get": {
          // enable the method
          "enabled": true, 
          "secured": true,
          "grants": ["get:users"]
        },
        "post": {
          // disable the method
          "enabled": false, 
          "secured": true,
          "grants": ["get:users"]
        },
...
```

### Toggle authentication

The Data Resource API makes use of [BrightHive authlib](https://github.com/brighthive/authlib) for adding authentication to endpoints. Authentication can be toggled on or off – on a per method basis. 

```JavaScript
{
  "api": {
    "resource": "name_of_endpoint",
    "methods": [
      {
        "get": {
          "enabled": true,
          // do not require authentication
          "secured": false,
          "grants": ["get:users"]
        },
        "post": {
          "enabled": false,
          // require authentication
          "secured": true, 
          "grants": ["get:users"]
        },
...
```

### Define the Table Schema

The Data Resource API utilizes [the Table Schema from fictionless data](https://frictionlessdata.io/specs/table-schema/). The Table Schema is represented by a "descriptor", or a JSON object with particular attributes. In a Data Resource schema, the descriptor occupies the value of "datastore" >> "schema". A schema can have up to four properties, among them: `primaryKey`, `foreignKeys`, and `fields`. 

The `fields` must be an array of JSON objects, and each object must define a field on the data model. A field definition should include, at minimum, a `name`, `type` (defaults to String), and `required` (defaults to `false`). 

Frictionless data and, correspondingly, the Data Resource API can be particular about what goes inside a field descriptor. `TABLESCHEMA_TO_SQLALCHEMY_TYPES` defines the available types in the frictionless schema and the corresponding types in sqlalchemy. Stick to these types, or you can anticipate unexpected behavior in your API! (See `data-resource-api/data_resource_api/factories/table_schema_types.py` for more context.)

```python
TABLESCHEMA_TO_SQLALCHEMY_TYPES = {
    'string': String,
    'number': Float,
    'integer': Integer,
    'boolean': Boolean,
    'object': String,
    'array': String, # Not supported yet
    'date': Date,
    'time': DateTime, # Not supported yet
    'datetime': DateTime,
    'year': Integer,
    'yearmonth': Integer, # Not supported yet
    'duration': Integer,
    'geopoint': String,
    'geojson': String, # Not supported yet
    'any': String
}
```

### Add foreign keys

Creating a foreign key involves making two additions to the JSON. 

First, add the foreign key as a field in the `schema`:

```JavaScript
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

```JavaScript
"datastore": {
  "tablename": "programs",
  "restricted_fields": [],
  "schema": {  
    "fields": [ 
      // Descriptor for location_id field, plus other fields
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

### Hide fields

Sometimes, a data resource has fields that contain important information (e.g., a source URL, a UUID) that should not be visible in the API. Hide these fields by adding the field `name` to the list of `restricted_fields`.

```JavaScript
"datastore": {
  "tablename": "programs",
  "restricted_fields" : ["location_id"],
...
```

### Many to many

To create a many to many resource add the relationship to the API section.

```JavaScript
{
  "api": {
    "resource": "programs",
    "methods": [
      {
        "custom": [
          {
            "resource": "/programs/credentials"
          }
        ]
      }
    ]
  },
  ...
```

This will generate a many to many relationship.

#### POST
To add a resource you would POST and in the body include the child field as a parameter.
]
#### GET
To query the relationship you have to go to `/programs/1/credentials`. The relationship will not currently show up if you simply query `/programs/1`.
,4

#### PUT
To replace the relationship perform a `PUT` to `/programs/1/credentials` with the full list of primary keys.

```json
{
  "credentials": [2,3]
}
```

#### PATCH
To append a primary key to the relationship list perform a `PATCH`. If you currently have a list of `"credentials": [1]` and you perform `PATCH` with `"credentials": [2,3]` it will return `"credentials":[1,2,3]`

#### DELETE
You can perform a `DELETE` that will remove the given items from the list. If you wish to remove all items perform a `PUT` with an empty list.

Given that you have a list of relationships, `[1,2,3,4,5]`:

Performing a `DELETE` with 
```
{
  "credentials": [2]
}
```

Results in `[1,3,4,5]`.

You can also give more than one item. Given that you have a list of relationships, `[1,2,3,4,5]` and we perform the following with `DELETE`
```
{
  "credentials": [1,3,5]
}
```

Results in `[2,4]`.


## Configuration

The following parameters can be adjusted to serve testing, development, or particular deployment needs. 

RELATIVE_PATH

ABSOLUTE_PATH

ROOT_PATH

MIGRATION_HOME

DATA_RESOURCE_SLEEP_INTERVAL

DATA_MODEL_SLEEP_INTERVAL

SQLALCHEMY_TRACK_MODIFICATIONS

PROPAGATE_EXCEPTIONS

POSTGRES_USER

POSTGRES_PASSWORD

POSTGRES_DATABASE

POSTGRES_HOSTNAME

POSTGRES_PORT

SQLALCHEMY_DATABASE_URI

OAUTH2_PROVIDER

OAUTH2_URL

OAUTH2_JWKS_URL

OAUTH2_AUDIENCE

OAUTH2_ALGORITHMS

SECRET_MANAGER

=======
## Running tests

A few tests within the test suite currently require a docker image to be spun up in order to pass the tests. In order for the tests to pass you simply need to have docker running.

For developers to run a test use the following,

1. First install the requirements
```bash
pipenv install --dev
```

2. Run the tests with the following command,
```bash
pipenv run pytest -c pytest.ini
```

## Troubleshooting
If you have trouble starting the application with `docker-compose up` the problem may lie in your postgres container.

Try running `docker rm postgres-container-id` to remove any prevoiusly saved data in the postgres container. This will allow the application to rebuild the database from scratch and should start successfully.

Or try running `docker system prune`.