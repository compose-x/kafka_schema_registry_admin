#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2020-2021 John Mille <john@ews-network.net>

import sys
from copy import deepcopy
from os import path
from time import sleep

import pytest
from testcontainers.compose import DockerCompose

from kafka_schema_registry_admin import SchemaRegistry
from kafka_schema_registry_admin.client_wrapper.errors import (
    IncompatibleSchema,
    NotFoundException,
)

HERE = path.abspath(path.dirname(__file__))

compose = DockerCompose(
    path.abspath(f"{HERE}/.."),
    compose_file_name="docker-compose.yaml",
    wait=True,
    pull=True,
)
compose.start()
sleep(5)

SR_PORT = int(compose.get_service_port("schema-registry", 8081))
BASE_URL = f"http://localhost:{SR_PORT}"

print(f"BASE URL FOR TESTS: {BASE_URL}")


@pytest.fixture()
def authed_local_registry():
    return SchemaRegistry(
        BASE_URL,
        **{"basic_auth.username": "confluent", "basic_auth.password": "confluent"},
    )


@pytest.fixture()
def local_registry():

    return SchemaRegistry(f"http://localhost:{SR_PORT}")


@pytest.fixture()
def schema_sample():
    return {
        "type": "record",
        "namespace": "com.mycorp.mynamespace",
        "name": "value_test_subject",
        "doc": "Sample schema to help you get started.",
        "fields": [
            {
                "name": "myField1",
                "type": "int",
                "doc": "The int type is a 32-bit signed integer.",
            },
            {
                "name": "myField2",
                "type": "double",
                "doc": "The double type is a double precision (64-bit) IEEE 754 floating-point number.",
            },
            {
                "name": "myField3",
                "type": "string",
                "doc": "The string is a unicode character sequence.",
            },
        ],
    }


def test_register_new_definition(authed_local_registry, schema_sample):
    c = authed_local_registry.post_subject_schema_version(
        "test-subject4", schema_sample
    )
    r = authed_local_registry.get_schema_from_id(c.json()["id"])
    assert "test-subject4" in authed_local_registry.subjects


def test_subject_existing_schema_definition(local_registry, schema_sample):
    r = local_registry.post_subject_schema("test-subject4", schema_sample, "AVRO")
    r = local_registry.get_schema_versions_from_id(r.json()["id"])


def test_register_new_definition_updated(local_registry, schema_sample):
    new_version = deepcopy(schema_sample)
    test = local_registry.post_subject_schema("test-subject4", schema_sample)
    latest = local_registry.get_subject_versions_referencedby(
        "test-subject4", test.json()["version"]
    )
    new_version["fields"].append(
        {
            "doc": "The string is a unicode character sequence.",
            "name": "myField4",
            "type": "string",
        }
    )
    with pytest.raises(NotFoundException):
        local_registry.get_compatibility_subject_config("test-subject4")
    local_registry.put_compatibility_subject_config("test-subject4", "BACKWARD")
    compat = local_registry.post_compatibility_subjects_versions(
        "test-subject4",
        test.json()["version"],
        new_version,
        "AVRO",
    )
    assert isinstance(compat.json()["is_compatible"], bool)
    is_compatible = compat.json()["is_compatible"]
    if is_compatible:
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, "AVRO"
        )
    with pytest.raises(IncompatibleSchema):
        new_version["fields"].append({"type": "string", "name": "surname"})
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, "AVRO"
        )
    local_registry.put_compatibility_subject_config("test-subject4", "FORWARD")
    new_version["fields"].pop(0)
    with pytest.raises(IncompatibleSchema):
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, "AVRO"
        )


def test_get_all_subjects(local_registry):
    r = local_registry.get_all_subjects().json()
    assert isinstance(r, list) and r


def test_get_all_schema_types(local_registry):
    r = local_registry.get_schema_types().json()
    assert isinstance(r, list) and r


def test_delete_subject(local_registry):
    local_registry.delete_subject("test-subject4", permanent=True)


def test_error_delete_subject(local_registry):
    with pytest.raises(NotFoundException):
        local_registry.delete_subject("test-subject4", permanent=True)
