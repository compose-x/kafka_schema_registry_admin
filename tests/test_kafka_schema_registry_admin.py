#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@ews-network.net>

import pytest
from requests.exceptions import HTTPError
from copy import deepcopy

from kafka_schema_registry_admin.kafka_schema_registry_admin import SchemaRegistry


@pytest.fixture()
def local_registry():
    return {
        "SchemaRegistryUrl": "http://localhost:8081",
        "Username": "confluent",
        "Password": "confluent",
    }


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


def test_register_new_definition(local_registry, schema_sample):
    s = SchemaRegistry(**local_registry)
    c = s.post_subject_version("test-subject4", schema_sample, "AVRO")
    r = s.get_schema_from_id(c["id"])


def test_subject_existing_schema_definition(local_registry, schema_sample):
    s = SchemaRegistry(**local_registry)
    r = s.post_subject_schema("test-subject4", schema_sample, "AVRO")
    print(r)


def test_register_new_definition_updated(local_registry, schema_sample):
    s = SchemaRegistry(**local_registry)
    new_version = deepcopy(schema_sample)
    test = s.post_subject_schema_version("test-subject4", schema_sample)
    latest = s.get_subject_versions_referencedby("test-subject4", test["version"])
    new_version["fields"].append(
        {
            "doc": "The string is a unicode character sequence.",
            "name": "myField4",
            "type": "string",
        }
    )
    compat = s.post_compatibility_subjects_versions(
        "test-subject4", test["version"], new_version, "AVRO", as_bool=True
    )
    assert isinstance(compat, bool)
    if compat:
        r = s.post_subject_version("test-subject4", new_version, "AVRO")
    with pytest.raises(HTTPError):
        new_version["fields"].append({"type": "string", "name": "surname"})
        r = s.post_subject_version("test-subject4", new_version, "AVRO")


def test_get_all_subjects(local_registry):
    s = SchemaRegistry(**local_registry)
    r = s.get_all_subjects()
    assert isinstance(r, list) and r


def test_get_all_schemas(local_registry):
    r = SchemaRegistry(**local_registry).get_all_schemas()
    assert isinstance(r, list) and r


def test_get_all_schema_types(local_registry):
    r = SchemaRegistry(**local_registry).get_schema_types()
    assert isinstance(r, list) and r


def test_delete_subject(local_registry):
    s = SchemaRegistry(**local_registry)
    s.delete_subject("test-subject4", permanent=True)


def test_error_delete_subject(local_registry):
    with pytest.raises(HTTPError):
        s = SchemaRegistry(**local_registry)
        s.delete_subject("test-subject4", permanent=True)
