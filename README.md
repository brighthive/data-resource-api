# Data Resource API

![Maintenance](https://img.shields.io/maintenance/yes/2020)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/brighthive/data-resource-api)
![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/brighthive/data-resource-api/v1.1.1)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/brighthive/data-resource-api)

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/brighthive/data-resource-api)
![CircleCI](https://img.shields.io/circleci/build/github/brighthive/data-resource-api)
![GitHub](https://img.shields.io/github/license/brighthive/data-resource-api)

<!-- ![Coveralls github](https://img.shields.io/coveralls/github/brighthive/data-resource-api) -->

![Twitter Follow](https://img.shields.io/twitter/follow/brighthiveio?style=social)

An elegant, opinionated framework for deploying BrightHive Data Resources (declarative database and API) with zero coding.

## Motivation
[BrightHive](https://brighthive.io) is in the business of building **Data Trusts**, which are *legal, technical, and governance frameworks that enable networks of organizations to securely and responsibly share and collaborate with data, generating new insights and increasing their combined impact.*

**Data Resources** are a core element of Data Trusts and may be loosely defined as *data that is owned by or stewarded over by members of Data Trusts.*

From the technical perspective, a BrightHive Data Resource is an entity comprised of the following elements:

- **Data Model** - The data model consists of one or more database tables and associated Object Relational Mapping (ORM) objects for communicating with these tables.
- **RESTful API** - Data managed by Data Resources are accessed via RESTful API endpoints. These endpoints support standard operations (i.e. **GET**, **POST**, **PUT**, **PATCH**, **DELETE**).
- **Data Resource Schemas** - Data Resource Schemas are JSON documents that define the data model, API endpoints, and security constraints placed on the specific Data Resource. These schemas are what allow for new Data Resources to be created without new code being written.

## Features

Simply provide the application a declarative database and API specification and it will automatically stand up a RESTful database and API!

- Declarative Database, including many to many
- Automatic REST API
- Enable/disable HTTP routes
- Automatic database migrations
- Hot reloading of database and API on migrations


## How to use Data Resource API

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

### Customize your JSON schema

The Data Resource API auto-magically instantiates data stores and corresponding endpoints without any coding.

Each JSON file in the `schema` directory delineates a resource, namely: its RESTful paths ("api"), and its data model ("datastore"). Create a new resource by adding another JSON file to the `schema` directory. (Visit the `schema` directory for example JSON files.)

See the [data resource api documentation](documentation.md) on setting up and modifying your JSON schema file.

## How to develop Data Resource API

> We welcome code contributions, suggestions, and reports! Please report bugs and make suggestions using Github issues. The BrightHive team will triage and prioritize your issue as soon as possible.

1. Install pipenv.
2. Install docker and docker-compose.
3. Clone the repo.
4. Run `pipenv install --dev`

### Troubleshooting
If you have trouble starting the application with `docker-compose up` the problem may lie in your postgres container.

Try running `docker rm postgres-container-id` to remove any prevoiusly saved data in the postgres container. This will allow the application to rebuild the database from scratch and should start successfully.

Or try running `docker system prune`.

## Testing
How do I run tests? (And what libraries did we use to write said tests?)

A few tests within the test suite currently require a docker image to be spun up in order to pass the tests. In order for the tests to pass you simply need to have docker running.

For developers to run a test use the following,

1. First install the requirements
```bash
pipenv install --dev
```

2. Run the tests with the following command,
```bash
pipenv run pytest
```

To leave the database up after running,
```bash
DR_LEAVE_DB=true pipenv run pytest
```

## Team
Names and titles of core contributors (including people who did not push code to Github). Use bullets, for example:

```
* Gregory Mundy (VP of Engineering)
* Logan Ripplinger (Software Engineer)
```

## License
[MIT](LICENSE)
