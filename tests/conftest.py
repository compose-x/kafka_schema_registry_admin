"""Pytest configuration and hooks"""

from os import path

from testcontainers.compose import DockerCompose

HERE = path.abspath(path.dirname(__file__))

compose = DockerCompose(
    path.abspath(f"{HERE}/.."), compose_file_name="docker-compose.yaml", wait=True
)


def pytest_sessionfinish(session, exitstatus):
    # compose.stop()
    print("Testing session has finished")
    print(f"Exit status: {exitstatus}")
