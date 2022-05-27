#
#   Copyright 2022 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Code to load and validate trait/specification definitions from
YAML declarations.
"""

import json
import jsonschema
import os
import yaml

from typing import List

from .datamodel import (
    PackageDefinition,
    SpecificationDefinition,
    TraitDefinition,
    PropertyDefinition,
    PropertyType,
)


def loadYAML(path: str) -> dict:
    """
    Loads specification and trait definitions from a YAML file.
    """
    with open(path, "r") as file:
        # It would be nice to take advantage of the auto-instantiation
        # of classes via the load(), but we can't really require
        # the addition of the `!!python/object` tag - as that would be
        # somewhat fragile.
        model = yaml.safe_load(file)
    return model


def validateModel(model: dict):
    """
    Validates the supplied model meets the specified schema.
    """
    jsonschema.validate(model, schema=__loadSchema())


def buildPackageDefinition(model: dict) -> PackageDefinition:
    """
    Populates a package definition from the supplied model.

    @param model A dict conforming to the codegen JSON schema. This
    should first be validated using the @ref modelMethod method.
    """
    packageId = model["package"]
    return PackageDefinition(
        id=packageId,
        description=model.get("description", ""),
        traits=__unpackTraits(model.get("traits", {}), packageId),
        specifications=__unpackSpecifications(model.get("specifications", {}), packageId),
    )


def __unpackSpecifications(model: dict, packageId: str) -> dict:
    """
    Returns a dict of namespaced SpecificationDefinitions from the
    supplied model.

    @param model A dict as per the "specifications" key in the JSON
    schema definition.
    """
    specifications = [
        SpecificationDefinition(
            id=f"{packageId}.{id_}",
            name=id_,
            description=data.get("description", ""),
            traitSet=data["traitSet"],
            usage=data.get("usage", []),
        )
        for id_, data in model.items()
    ]
    return __buildNamespace(specifications)


def __unpackTraits(model: dict, packageId: str) -> dict:
    """
    Returns a dict of namespaced TraitDefinitions from the supplied
    model.

    @param model A dict as per the "specifications" key in the JSON
    schema definition.
    """
    traits = [
        TraitDefinition(
            id=f"{packageId}.{id_}",
            name=id_,
            description=data.get("description", ""),
            properties=__unpackProperties(data.get("properties", {})),
            usage=data.get("usage", []),
        )
        for id_, data in model.items()
    ]
    return __buildNamespace(traits)


def __unpackProperties(model) -> List:
    """
    Returns a list of PropertyDefinitions sorted by id.

    @param model A dict as per the "properties" key under a trait
    definition in the JSON schema definition.
    """
    properties = [
        PropertyDefinition(
            id=id_, type=PropertyType(data["type"]), description=data.get("description", "")
        )
        for id_, data in model.items()
    ]
    properties.sort(key=lambda d: d.id)
    return properties


def __buildNamespace(definitions: List) -> dict:
    """
    Returns a namespace represented as a dict of dicts from
    the usage properties of the supplied definitions.
    """
    namespaces = {}
    for definition in definitions:
        namespace = definition.usage[0] if len(definition.usage) == 1 else ""
        namespaces.setdefault(namespace, []).append(definition)
    for definitions in namespaces.values():
        definitions.sort(key=lambda d: d.id)
    return namespaces


def __loadSchema() -> dict:
    """
    Loads the validation schema
    """
    path = os.path.join(__rootDir, "schema.json")
    with open(path, "r") as file:
        return json.load(file)


__rootDir = os.path.dirname(__file__)
