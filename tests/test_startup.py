"""Database Unit Test.

"""

import docker
import requests 
from expects import expect, be, be_empty, equal

class TestDatabase(object):
    """Database Configuration Unit Tests"""

    def test_docker_running(self, psql_docker, dr_docker, dr_manager_docker):
        """Run docker containers and test that they return data."""
        psql_docker.start_postgresql_container()
        dr_docker.start_container()
        dr_manager_docker.start_container()
        
        docker_client = docker.from_env()
        containers = docker_client.containers.list()

        running_status = {}
        for c in containers:
            running_status[c.name] = c.status

        expect(running_status['data-resource-api-test_manager']).to(equal('running'))
        expect(running_status['data-resource-api-test']).to(equal('running'))
        expect(running_status['postgres-test']).to(equal('running'))

    def test_connection(self, psql_docker, dr_docker, dr_manager_docker):
        psql_docker.start_postgresql_container()
        dr_docker.start_container()
        dr_manager_docker.start_container()

        # Need to wait for the data resource to spin up
        dr_manager_docker.wait_for_ready()

        credentials_url = "http://0.0.0.0:8000/credentials"
        r = requests.get(url=credentials_url) 
        data = r.json()
        print(data)
        
        expect(data['credentials']).to(be_empty)
        expect(data['links']).to(be_empty)

        programs_url = "http://0.0.0.0:8000/programs"
        r = requests.get(url=programs_url) 
        data = r.json()
        print(data)

        expect(data['message']).to(equal('Access Denied'))
