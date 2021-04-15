#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-3.0-only
# Copyright 2021 John Mille <john@ews-network.net>

"""The setup script."""

import os
import re
from setuptools import setup, find_packages

DIR_HERE = os.path.abspath(os.path.dirname(__file__))
# REMOVE UNSUPPORTED RST syntax
REF_REGX = re.compile(r"(\:ref\:)")

try:
    with open(f"{DIR_HERE}/README.rst", encoding="utf-8") as readme_file:
        readme = readme_file.read()
        readme = REF_REGX.sub("", readme)
except FileNotFoundError:
    readme = "Schema Registry Admin API Client"

try:
    with open(f"{DIR_HERE}/HISTORY.rst", encoding="utf-8") as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = "Latest packaged version."

requirements = []
with open(f"{DIR_HERE}/requirements.txt", "r") as req_fd:
    for line in req_fd:
        requirements.append(line.strip())

test_requirements = []
try:
    with open(f"{DIR_HERE}/requirements_dev.txt", "r") as req_fd:
        for line in req_fd:
            test_requirements.append(line.strip())
except FileNotFoundError:
    print("Failed to load dev requirements. Skipping")

setup_requirements = []

setup(
    author="JohnPreston",
    author_email="john@ews-network.net",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=requirements,
    license="LGPL-3.0-only",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="kafka schema-registry admin api",
    name="kafka_schema_registry_admin",
    packages=find_packages(
        include=["kafka_schema_registry_admin", "kafka_schema_registry_admin.*"]
    ),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/johnpreston/kafka_schema_registry_admin",
    version="0.0.2",
    zip_safe=False,
)
