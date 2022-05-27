#
#   Copyright 2013-2022 [The Foundry Visionmongers Ltd]
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
A codegen generator that outputs a python package.
"""

import os
import keyword
import jinja2


from . import helpers
from ..datamodel import PropertyType

__typeMap = {
    PropertyType.kString: "str",
    PropertyType.kInteger: "int",
    PropertyType.kFloat: "float",
    PropertyType.kBool: "bool",
    PropertyType.kDict: "openassetio.InfoDictionary",
}


def installCustomFilters(environment):
    def validateIdentifier(string: str, original: str):
        if not string.isidentifier():
            raise ValueError(f"{string}' (from '{original}' is not a valid python identifier.")
        if keyword.iskeyword(string):
            raise ValueError(f"{string}' (from '{original}' is a reserved python keyword.")

    def toPyClassName(string: str):
        className = helpers.toUpperCamelAlnum(string)
        validateIdentifier(className, string)
        return className

    def toPyVarName(string: str):
        varName = helpers.toLowerCamelAlnum(string)
        validateIdentifier(varName, string)
        return varName

    def toPyType(modelType):
        return __typeMap[modelType]

    environment.filters["toUpperCamelAlnum"] = helpers.toUpperCamelAlnum
    environment.filters["toPyClassName"] = toPyClassName
    environment.filters["toPyVarName"] = toPyVarName
    environment.filters["toPyType"] = toPyType


def generate(packageDefinition, outputDirPath, isVerbose):
    """
    Generates a python package for the supplied definition under outputDirPath.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("openassetio.codegen"))
    installCustomFilters(env)

    packageDirPath = os.path.join(outputDirPath, packageDefinition.id)
    if isVerbose:
        print(packageDirPath)
    os.makedirs(packageDirPath, exist_ok=True)

    initTemplate = env.get_template(os.path.join("python", "init.py.in"))
    with open(os.path.join(packageDirPath, "__init__.py")) as file:
        file.write(initTemplate.render({"package": packageDefinition}))

    for kind, namespaces in (("traits", packageDefinition.traits),):

        template = env.get_template(os.path.join("python", f"{kind}.py.in"))

        if not namespaces:
            continue

        # Make the module directory
        kindDirPath = os.path.join(packageDirPath, kind)
        if isVerbose:
            print(kindDirPath)
        os.makedirs(kindDirPath, exist_ok=True)

        for namespace, declarations in namespaces.items():
            modulePath = os.path.join(kindDirPath, f"{namespace or '__init__'}.py")
            if isVerbose:
                print(modulePath)
            with open(modulePath, "w") as file:
                file.write(
                    template.render(
                        {
                            "package": packageDefinition,
                            "namespace": namespace,
                            "declarations": declarations,
                        }
                    )
                )

        # Ensure we have __init__.py if we had no top-level namespace
        # definitions to make.
        initPath = os.path.join(kindDirPath, "__init__.py")
        if not os.path.exists(initPath):
            if isVerbose:
                print(initPath)
            open(initPath, "a").close()
