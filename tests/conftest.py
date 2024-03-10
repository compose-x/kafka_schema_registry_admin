"""Pytest configuration and hooks"""

from os import path

import pytest
from testcontainers.compose import DockerCompose

from kafka_schema_registry_admin import SchemaRegistry

HERE = path.abspath(path.dirname(__file__))


docker_compose = DockerCompose(
    path.abspath(f"{HERE}/.."),
    compose_file_name="docker-compose.yaml",
    wait=True,
    pull=True,
)

docker_compose.stop(down=True)
docker_compose.start()
sr_port = int(docker_compose.get_service_port("schema-registry", 8081))
base_url: str = f"http://localhost:{sr_port}"
docker_compose.wait_for(f"{base_url}/subjects")


@pytest.fixture(scope="session")
def local_registry():
    return SchemaRegistry(base_url)


@pytest.fixture(scope="session")
def authed_local_registry():
    return SchemaRegistry(
        base_url,
        **{"basic_auth.username": "confluent", "basic_auth.password": "confluent"},
    )


def pytest_sessionfinish(session, exitstatus):
    docker_compose.stop()
    print("Testing session has finished")
    print(f"Exit status: {exitstatus}")
