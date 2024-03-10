# SPDX-License-Identifier: Apache License 2.0
# Copyright 2021 John Mille <john@ews-network.net>

"""
Main module for schema_registry_admin
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response

import json
from enum import Enum
from logging import getLogger

import requests

from .client_wrapper import Client
from .client_wrapper.errors import NotFoundException

LOG = getLogger()
LOG.setLevel("WARN")


class Type(Enum):
    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUFF = "PROTOBUF"


class SchemaRegistry:

    def __init__(self, base_url: str, *args, **kwargs):
        username = kwargs.get("basic_auth.username", None)
        password = kwargs.get("basic_auth.password", None)
        basic_auth: dict = {}
        if username and password:
            basic_auth: dict = {
                "basic_auth.username": username,
                "basic_auth.password": password,
            }
        self.client: Client = Client(str(base_url), basic_auth)

    @property
    def subjects(self) -> list[str]:
        """
        Property to get the list of subjects in the schema registry
        """
        return self.get_all_subjects().json()

    def get_all_subjects(self) -> Response:
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects

        :raises: requests.exceptions.HTTPError
        """
        return self.client.get("/subjects")

    def get_subject_versions(self, subject_name: str) -> Response:
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions

        :raises: requests.exceptions.HTTPError
        """
        return self.client.get(f"/subjects/{subject_name}/versions")

    def get_subject_versions_referencedby(self, subject_name, version_id) -> Response:
        """
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html
        #get--subjects-(string-%20subject)-versions-versionId-%20version-referencedby

        :param str subject_name:
        :param int version_id:
        :return: the request
        """
        req = self.client.get(
            f"/subjects/{subject_name}/versions/{version_id}/referencedby"
        )
        return req

    def post_subject_schema(
        self, subject_name, definition, schema_type=None
    ) -> Response:
        """Returns the schema ID and details if already exists, from the schema definition"""
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        url = f"/subjects/{subject_name}"
        req = self.client.post(url, json=payload)

        return req

    def post_subject_schema_version(
        self, subject_name, definition, schema_type=None
    ) -> Response:
        try:
            return self.post_subject_schema(subject_name, definition, schema_type)
        except NotFoundException:
            if isinstance(definition, dict):
                definition = str(json.dumps(definition))
            if schema_type is None:
                schema_type = Type["AVRO"].value
            else:
                schema_type = Type[schema_type].value

            payload = {"schema": definition, "schemaType": schema_type}
            url = f"/subjects/{subject_name}/versions"
            try:
                req = self.client.post(url, json=payload)
                return req
            except Exception as error_create:
                print("ERROR CREATE", error_create)
                raise

    def delete_subject(
        self, subject_name, version_id=None, permanent=False
    ) -> Response:
        """
        Method to delete a subject via its ID
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#delete--subjects-(string-%20subject)

        :param str subject_name:
        :param int version_id:
        :param bool permanent:
        """
        url = f"/subjects/{subject_name}"
        if version_id:
            url = f"{url}/versions/{version_id}"
        req = self.client.delete(url)
        if permanent:
            permanent_url = f"{url}?permanent=true"
            req = self.client.delete(permanent_url)
        return req

    def get_schema_types(self) -> Response:
        """
        Method to get the list of schema types and return the request object
        """
        url = f"/schemas/types"
        req = self.client.get(url)
        return req

    def get_schema_from_id(self, schema_id) -> Response:
        url = f"/schemas/ids/{schema_id}"
        LOG.debug(url)
        req = self.client.get(url)
        return req

    def get_schema_versions_from_id(self, schema_id):
        """
        Retrieve the versions for a given schema by its ID
        """
        url = f"/schemas/ids/{schema_id}/versions"
        req = self.client.get(url)
        return req

    def post_compatibility_subjects_versions(
        self,
        subject_name,
        version_id,
        definition,
        schema_type=None,
        references=None,
    ) -> Response:
        url = f"/compatibility/subjects/{subject_name}/versions/{version_id}"
        LOG.debug(url)
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        if references and isinstance(references, list):
            payload["references"] = references

        req = self.client.post(url, json=payload)
        return req

    def get_compatibility_subject_config(self, subject_name) -> Response:
        url = f"/config/{subject_name}/"
        req = self.client.get(url)
        return req

    def put_compatibility_subject_config(self, subject_name, compatibility) -> Response:
        url = f"/config/{subject_name}/"
        payload = {"compatibility": compatibility}
        req = self.client.put(url, json=payload)
        return req
