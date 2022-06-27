# SPDX-License-Identifier: LGPL-3.0-only
# Copyright 2021 John Mille <john@ews-network.net>

"""
Main module for schema_registry_admin
"""

import json
from enum import Enum
from logging import getLogger
from typing import List, Optional

import requests
from pydantic import AnyUrl, BaseModel, Extra, Field

LOG = getLogger()
LOG.setLevel("WARN")


class Type(Enum):
    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUFF = "PROTOBUF"


class DefinitionDocument(BaseModel):
    class Config:
        extra = Extra.allow

    name: str
    namespace: str
    fields: List


class SchemaRegistry(BaseModel):
    SchemaRegistryUrl: Optional[AnyUrl] = Field(
        None,
        description="Endpoint URL of the Schema Registry",
    )
    Username: Optional[str] = Field("", description="Username for Authentication")
    Password: Optional[str] = Field("", description="Password for Authentication")

    default_headers = {
        "Accept": "application/json",
    }
    post_headers = {
        "Accept": "application/json",
        "Content-Type": "application/vnd.schemaregistry.v1+json",
    }

    def __init__(self, **data):
        super().__init__(**data)
        if (self.Username and not self.Password) or (
            self.Password and not self.Username
        ):
            raise KeyError(
                "When specifying credentials, you must specify both Username and Password"
            )

    def get_all_subjects(self):
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects

        :raises: requests.exceptions.HTTPError
        """
        url = f"{self.SchemaRegistryUrl}/subjects"
        LOG.debug(url)
        if not self.Username:
            req = requests.get(url)
        else:
            req = requests.get(url, auth=(self.Username, self.Password))
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_subject_versions(self, subject_name: str):
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions

        :raises: requests.exceptions.HTTPError
        """
        url = f"{self.SchemaRegistryUrl}/subjects/{subject_name}/versions"
        LOG.debug(url)
        if not self.Username:
            req = requests.get(url)
        else:
            req = requests.get(url, auth=(self.Username, self.Password))
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_all_schemas(self):
        """
        Method to get all the schemas in the schema registry

        :raises: requests.exceptions.HTTPError
        :return:
        """
        url = f"{self.SchemaRegistryUrl}/schemas"
        LOG.debug(url)
        if not self.Username:
            req = requests.get(url)
        else:
            req = requests.get(url, auth=(self.Username, self.Password))
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_subject_versions_referencedby_raw(self, subject_name, version_id):
        """
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html
        #get--subjects-(string-%20subject)-versions-versionId-%20version-referencedby

        :param str subject_name:
        :param int version_id:
        :return: the request
        """
        url = f"{self.SchemaRegistryUrl}/subjects/{subject_name}/versions/{version_id}/referencedby"
        LOG.debug(url)
        if not self.Username:
            req = requests.get(url, headers=self.default_headers)
        else:
            req = requests.get(
                url,
                headers=self.default_headers,
                auth=(self.Username, self.Password),
            )
        return req

    def get_subject_versions_referencedby(self, subject_name, version_id):
        """
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html
        #get--subjects-(string-%20subject)-versions-versionId-%20version-referencedby

        :param str subject_name:
        :param int version_id:
        :return:
        :raises: requests.exceptions.HTTPError
        """
        req = self.get_subject_versions_referencedby_raw(subject_name, version_id)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def post_subject_schema(
        self, subject_name, definition, schema_type=None, for_key=False
    ):
        """
        Method that returns the schema ID and details if already exists, from the schema definition

        :param str subject_name:
        :param definition:
        :param schema_type:
        :return:
        :raises: requests.exceptions
        """
        if not for_key:
            subject_name = f"{subject_name}-value"
        else:
            subject_name = f"{subject_name}-key"
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        url = f"{self.SchemaRegistryUrl}/subjects/{subject_name}"
        LOG.debug(url)
        if not self.Username:
            req = requests.post(url, json=payload, headers=self.post_headers)
        else:
            req = requests.post(
                url,
                json=payload,
                headers=self.post_headers,
                auth=(self.Username, self.Password),
            )
        return req

    def post_subject_version_raw(self, subject_name, definition, schema_type=None):
        exists_req = self.post_subject_schema(subject_name, definition, schema_type)
        if exists_req.status_code == 200:
            return exists_req
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        url = f"{self.SchemaRegistryUrl}/subjects/{subject_name}/versions"
        LOG.debug(url)
        if not self.Username:
            req = requests.post(url, json=payload, headers=self.post_headers)
        else:
            req = requests.post(
                url,
                json=payload,
                headers=self.post_headers,
                auth=(self.Username, self.Password),
            )
        return req

    def post_subject_version(
        self, subject_name, definition, schema_type=None, for_key=False
    ):
        if not for_key:
            subject_name = f"{subject_name}-value"
        else:
            subject_name = f"{subject_name}-key"

        req = self.post_subject_version_raw(subject_name, definition, schema_type)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def post_subject_schema_version(self, subject_name, definition, schema_type=None):
        """
        Method to return the object response. Raise if not 200

        :param str subject_name:
        :param definition:
        :param str schema_type:
        :return: the content of the reply
        :rtype: dict
        :raises: requests.exceptions
        """
        req = self.post_subject_version_raw(subject_name, definition, schema_type)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def delete_subject_raw(self, subject_name, version_id=None, permanent=False):
        """
        Method to delete a subject via its ID
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#delete--subjects-(string-%20subject)

        :param str subject_name:
        :param int version_id:
        :param bool permanent:
        """
        url = f"{self.SchemaRegistryUrl}/subjects/{subject_name}"
        if version_id:
            url = f"{url}/versions/{version_id}"
        LOG.debug(url)
        if self.Username:

            req = requests.delete(url, auth=(self.Username, self.Password))
            if permanent:
                permanent_url = f"{url}?permanent=true"
                req = requests.delete(
                    permanent_url, auth=(self.Username, self.Password)
                )
        else:
            req = requests.delete(url)
            if permanent:
                permanent_url = f"{url}?permanent=true"
                req = requests.delete(permanent_url)
        return req

    def delete_subject(
        self, subject_name, version_id=None, permanent=False, for_key=False
    ):
        if not for_key:
            subject_name = f"{subject_name}-value"
        else:
            subject_name = f"{subject_name}-key"

        req = self.delete_subject_raw(subject_name, version_id, permanent)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_schema_types_raw(self):
        """
        Method to get the list of schema types and return the request object
        """
        url = f"{self.SchemaRegistryUrl}/schemas/types"
        LOG.debug(url)
        if self.Username:
            req = requests.get(url, auth=(self.Username, self.Password))
        else:
            req = requests.get(url)
        return req

    def get_schema_types(self):
        """
        Method to retrieve the supported schema types by the schema registry

        :return: list of schema types
        :rtype: list<str>
        """
        req = self.get_schema_types_raw()
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_schema_from_id_raw(self, schema_id):
        url = f"{self.SchemaRegistryUrl}/schemas/ids/{schema_id}"
        LOG.debug(url)
        if self.Username:
            req = requests.get(
                url, headers=self.default_headers, auth=(self.Username, self.Password)
            )
        else:
            req = requests.get(url, headers=self.default_headers)
        return req

    def get_schema_from_id(self, schema_id):
        """
        Method to return the object return from the request

        :param int schema_id:
        :return:
        """
        req = self.get_schema_from_id_raw(schema_id)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def get_schema_versions_from_id_raw(self, schema_id):
        """
        Method to retrieve the versions for a given schema by its ID

        :param schema_id:
        :return:
        """
        url = f"{self.SchemaRegistryUrl}/schemas/ids/{schema_id}/versions"
        LOG.debug(url)
        if self.Username:
            req = requests.get(
                url, headers=self.default_headers, auth=(self.Username, self.Password)
            )
        else:
            req = requests.get(url, headers=self.default_headers)
        return req

    def get_schema_versions_from_id(self, schema_id):
        """
        Method to get the content response as dict

        :param int schema_id:
        :return: the object
        :rtype: dict
        """
        req = self.get_schema_versions_from_id_raw(schema_id)
        if req.status_code == 200:
            return req.json()
        req.raise_for_status()

    def post_compatibility_subjects_versions_raw(
        self,
        subject_name,
        version_id,
        definition,
        schema_type=None,
        references=None,
    ):
        url = f"{self.SchemaRegistryUrl}/compatibility/subjects/{subject_name}/versions/{version_id}"
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

        if self.Username:
            req = requests.post(
                url,
                headers=self.post_headers,
                json=payload,
                auth=(self.Username, self.Password),
            )
        else:
            req = requests.post(url, headers=self.post_headers, json=payload)
        return req

    def post_compatibility_subjects_versions(
        self,
        subject_name,
        version_id,
        definition,
        definition_type=None,
        references=None,
        as_bool=False,
        for_key=False,
    ):
        if not for_key:
            subject_name = f"{subject_name}-value"
        else:
            subject_name = f"{subject_name}-key"

        req = self.post_compatibility_subjects_versions_raw(
            subject_name, version_id, definition, definition_type, references
        )
        if req.status_code == 200:
            if as_bool:
                return req.json()["is_compatible"]
            return req
        req.raise_for_status()
