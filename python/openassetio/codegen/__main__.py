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
Entry point for command-line execution of the specification/trait
codegen tool.
"""

# pylint: disable=invalid-name

import argparse
import inspect
import sys

from . import parser
from .generators import python

def __dumpPackageDefinition(package):
    def __dumpDefinitions(namespaces):
        out = ""
        for namespace in sorted(list(namespaces.keys())):
            indent = "  "
            if namespace:
                out += f"{indent}{namespace}:\n"
                indent = "    "
            for definition in namespaces[namespace]:
                out += f"{indent}- {definition.name}\n"
        return out

    out = f"Package: {package.id}\n"
    if package.traits:
        out += "Traits:\n"
        out += __dumpDefinitions(package.traits)
    if package.specifications:
        out += "Specifications:\n"
        out += __dumpDefinitions(package.specifications)
    return out


cmdline = argparse.ArgumentParser(
    prog="openassetio-codegen",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=inspect.cleandoc(
        """
        The openassetio-codegen utility generates code that provides
        strongly-typed views on an openassetio traits data instance. The
        tool is capable of generating code in a number of languages from the
        supplied file, containing the simplified declaration of one or more
        traits or specifications using the OpenAssetIO traits and
        specification declaration schema.

        By default, code is generated for all supported unless one or more
        language flags are specified.
        """
    ),
)

cmdline.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    help="Load and verify the supplied declarations without generating any code",
)

cmdline.add_argument("input", help="YAML file detailing traits and specifications to generate")

cmdline.add_argument(
    "-o",
    "--output-dir",
    required=True,
    help="Generate code under the supplied directory, the utility will attempt to created this"
    " directory if it does not exist",
)

cmdline.add_argument("--python", action="store_true", help="Generate Python classes")

cmdline.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Prints a description of the traits and specifications to stderr, and the path to"
    " each file generated file to stdout.",
)

args = cmdline.parse_args()


model = parser.loadYAML(args.input)
parser.validateModel(model)
packageDefinition = parser.buildPackageDefinition(model)

if args.verbose:
    sys.stderr.write(__dumpPackageDefinition(packageDefinition))

if args.dry_run:
    sys.exit(0)

# Python generation
if args.verbose:
    sys.stderr.write("Generating Python...\n")
python.generate(packageDefinition, args.output_dir, args.verbose)
