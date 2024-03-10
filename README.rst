===========================
Kafka schema registry admin
===========================

Simple / light HTTP client library (using requests) to manipulate schemas and definitions into Schema Registry.

* Confluent API specification is documented `here <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#overview>`__

* RedPanda API specification is documented `here <https://docs.redpanda.com/current/manage/schema-reg/schema-reg-api/>`__

.. warning::

    RedPanda SR does not have 100% compatibility with Confluent's.
    Confluent Cloud specific endpoints not implemented (and no plans to be).


Usage
======

Very simple example to manipulate the schema registry and its resources.
Every function returns the ``requests.Response`` object to allow you to implement any kind of logic from there,
instead of trying to implement it for you.

Non 2xx HTTP codes raise exceptions which are in the ``kafka_schema_registry_admin.client_wrapper.errors``
More specific exceptions will be created in due course to identify exact exceptions.

.. code-block::

    from kafka_schema_registry_admin import SchemaRegistry

    registry = SchemaRegistry("http://localhost:8081")
    subjects = registry.get_all_subjects().json()
