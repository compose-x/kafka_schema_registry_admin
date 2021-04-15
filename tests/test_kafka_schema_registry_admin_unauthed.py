# #   -*- coding: utf-8 -*-
# #  SPDX-License-Identifier: MPL-2.0
# #  Copyright 2020-2021 John Mille <john@ews-network.net>
#
# import pytest
# from requests.exceptions import HTTPError
# from copy import deepcopy
#
# from kafka_schema_registry_admin.kafka_schema_registry_admin import SchemaRegistry
#
#
# @pytest.fixture()
# def local_registry():
#     return {"SchemaRegistryUrl": "http://localhost:8081"}
#
#
# @pytest.fixture()
# def schema_sample():
#     return {
#         "type": "record",
#         "name": "testabcd",
#         "namespace": "abcd",
#         "fields": [{"type": "string", "name": "user"}, {"type": "int", "name": "age"}],
#     }
#
#
# def test_missing_parameter(local_registry):
#     with pytest.raises(KeyError):
#         missing_username = local_registry.copy()
#         missing_username["Password"] = "dummy"
#         SchemaRegistry(**missing_username)
#     with pytest.raises(KeyError):
#         missing_username = local_registry.copy()
#         missing_username["Username"] = "dummy"
#         SchemaRegistry(**missing_username)
#
#
# def test_register_new_definition(
#     local_registry, schema_sample
# ):
#     s = SchemaRegistry(**local_registry)
#     c = s.post_subject_version("test-subject", schema_sample, "AVRO")
#     r = s.get_schema_from_id(c["id"])
#
#
# def test_subject_existing_schema_definition(local_registry, schema_sample):
#     s = SchemaRegistry(**local_registry)
#     r = s.post_subject_schema("test-subject", schema_sample, "AVRO")
#
#
# def test_register_new_definition_updated(local_registry, schema_sample):
#     s = SchemaRegistry(**local_registry)
#     new_version = deepcopy(schema_sample)
#     new_version["fields"].append({"type": "string", "name": "surname"})
#     test = s.post_subject_schema_version("test-subject", schema_sample)
#     latest = s.get_subject_versions_referencedby("test-subject", test["version"])
#     compat = s.post_compatibility_subjects_versions(
#         "test-subject", test["version"], new_version, "AVRO", as_bool=True
#     )
#     assert isinstance(compat, bool)
#     with pytest.raises(HTTPError):
#         r = s.post_subject_version("test-subject", new_version, "AVRO")
#
#
# def test_get_all_subjects(local_registry):
#     s = SchemaRegistry(**local_registry)
#     r = s.get_all_subjects()
#     assert isinstance(r, list) and r
#
#
# def test_get_all_schemas(local_registry):
#     r = SchemaRegistry(**local_registry).get_all_schemas()
#     assert isinstance(r, list) and r
#
#
# def test_get_all_schema_types(local_registry):
#     r = SchemaRegistry(**local_registry).get_schema_types()
#     assert isinstance(r, list) and r
#
#
# def test_delete_subject(local_registry):
#     s = SchemaRegistry(**local_registry)
#     s.delete_subject("test-subject", permanent=True)
#
#
# def test_error_delete_subject(local_registry):
#     with pytest.raises(HTTPError):
#         s = SchemaRegistry(**local_registry)
#         s.delete_subject("test-subject", permanent=True)
