===========================
Kafka schema registry admin
===========================

Simple / light HTTP client library (using requests) to manipulate schemas and definitions into Schema Registry.

* Confluent API specification is documented `here <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#overview>`__

* RedPanda API specification is documented `here <https://docs.redpanda.com/current/manage/schema-reg/schema-reg-api/>`__


Usage
======

Very simple example to manipulate the schema registry and its resources.

.. code-block::

    from kafka_schema_registry_admin import SchemaRegistry

    registry = SchemaRegistry("http://localhost:8081")
    subjects = registry.get_all_subjects()
    schemas = registry.get_all_schemas()
