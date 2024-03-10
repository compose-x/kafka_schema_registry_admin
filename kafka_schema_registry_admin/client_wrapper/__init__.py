# SPDX-License-Identifier: Apache License 2.0
# Copyright 2021 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response

from urllib.parse import urlparse

import requests

from .errors import ApiGenericException, SchemaRegistryApiException, evaluate_api_return


class Client:
    """API Client wrapper around the requests"""

    def __init__(self, base_url: str):
        self._base_url = base_url

        self._default_headers: dict = {
            "Accept": "application/json",
        }
        self._post_headers: dict = {
            "Accept": "application/json",
            "Content-Type": "application/vnd.schemaregistry.v1+json",
        }

    @evaluate_api_return
    def get(self, api_path: str, *args, **kwargs) -> Response:
        """Get the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()

        response = requests.get(url, *args, **kwargs)
        return response

    @evaluate_api_return
    def post(self, api_path: str, *args, **kwargs) -> Response:
        """POST the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        headers.update(self._post_headers)
        url: str = urlparse(self._base_url + api_path).geturl()
        print("URL??", url)
        response = requests.post(url, *args, **kwargs)
        return response

    @evaluate_api_return
    def put(self, api_path: str, *args, **kwargs) -> Response:
        """PUT the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()

        response = requests.put(url, *args, **kwargs)
        return response

    @evaluate_api_return
    def delete(self, api_path: str, *args, **kwargs) -> Response:
        """DELETE the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)

        url: str = urlparse(self._base_url + api_path).geturl()
        response = requests.delete(url, *args, **kwargs)
        return response
