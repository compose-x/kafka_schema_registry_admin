# SPDX-License-Identifier: Apache License 2.0
# Copyright 2021 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from requests import exceptions as req_exceptions


def keyisset(_key: Any, _dict: dict):
    return isinstance(_dict, dict) and _dict.get(_key, False)


class ApiGenericException(Exception):
    """
    Generic class handling Exceptions
    """

    def __init__(self, msg, code, details):
        """

        :param msg:
        :param code:
        :param details:
        """
        super().__init__(msg, code, details)
        self.code = code
        self.details = details


class GenericNotFound(ApiGenericException):
    """
    Generic option for 404 return code
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class IncompatibleSchema(ApiGenericException):
    """
    Generic option for 409 return code and message starting
    with "Schema being registered is incompatible with an earlier schema for subject"
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class GenericConflict(ApiGenericException):
    """
    Generic option for 409 return code
    """

    def __init__(self, code, details):
        print(details[-1], type(details[-1]))
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            if isinstance(details[-1], dict) and keyisset("message", details[-1]):
                error_message = details[-1]["message"]
                if error_message.startswith(
                    "Schema being registered is incompatible with an earlier schema for subject"
                ):
                    raise IncompatibleSchema(code, details)
            super().__init__(details, code, details[1:])


class GenericUnauthorized(ApiGenericException):
    """
    Generic option for 401 return code
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class GenericForbidden(ApiGenericException):
    """
    Generic exception for a 403
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            super().__init__(details, code, details[1:])


class SchemaRegistryApiException(ApiGenericException):
    """
    Top class for DatabaseUser exceptions
    """

    def __init__(self, code, details):
        if code == 409:
            raise GenericConflict(code, details)
        elif code == 404:
            raise GenericNotFound(code, details)
        elif code == 401:
            raise GenericUnauthorized(code, details)
        elif code == 403:
            raise GenericForbidden(code, details)
        elif code == 409:
            raise GenericConflict(code, details)

        super().__init__(details[0], code, details[1])


def evaluate_api_return(function):
    """
    Decorator to evaluate the requests payload returned
    """

    def wrapped_answer(*args, **kwargs):
        """
        Decorator wrapper
        """
        try:
            payload = function(*args, **kwargs)
            if payload.status_code not in [200, 201, 202, 204] and not keyisset(
                "ignore_failure", kwargs
            ):
                try:
                    details = (args[0:2], payload.json())
                except req_exceptions.JSONDecodeError:
                    details = (args[0:2], payload.text)
                raise SchemaRegistryApiException(payload.status_code, details)

            elif keyisset("ignore_failure", kwargs):
                return payload
            return payload
        except req_exceptions.RequestException as error:
            print(error)
            raise

    return wrapped_answer
