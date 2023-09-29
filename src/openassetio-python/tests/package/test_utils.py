#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.utils namespace.
"""
import os

# pylint: disable=invalid-name,redefined-outer-name, too-few-public-methods
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio import utils
from openassetio.errors import InputValidationException
from openassetio.utils import PathType


class Test_PathType_enum:
    def test_expected_constants_are_unique_and_exhaustive(self):
        for i, enum in enumerate(
            (PathType.kSystem, PathType.kPOSIX, PathType.kWindows)
        ):
            assert int(enum) == i


class Test_pathToFileURL_pathFromFileURL_roundtrip:
    @pytest.mark.parametrize(
        "path_type", (PathType.kSystem, PathType.kPOSIX, PathType.kWindows)
    )
    def test_when_input_valid_then_produces_expected_values(self, path_type):

        # For extended windows paths
        long_path_string = r"\a\long\path" * 26
        long_path_url_string = long_path_string.replace("\\", "/")

        expected_results = {
            PathType.kPOSIX: (
                (
                    "/Testing/exr/cathedral/cathedral_withdisparity_%V.####.exr",
                    "file:///Testing/exr/cathedral/cathedral_withdisparity_%25V.%23%23%23%23.exr",
                ),
                (
                    "/D:/pretending/to/be/windows",
                    "file:///D:/pretending/to/be/windows",
                ),
                (
                    "/i /am/an awkäd/🎃 uniĆø∂e/path",
                    "file:///i%20/am/an%20awk%C3%A4d/%F0%9F%8E%83%20uni%C4%86%C3%B8%E2%88%82e/path",
                ),
            ),
            PathType.kWindows: (
                (
                    r"\\laptop\My Documents\FileSchemeURIs.doc",
                    "file://laptop/My%20Documents/FileSchemeURIs.doc",
                ),
                (
                    r"\\laptop\C$\My Documents\FileSchemeURIs.doc",
                    "file://laptop/C:/My%20Documents/FileSchemeURIs.doc",
                ),
                (
                    r"C:\Documents and Settings\FileSchemeURIs.doc",
                    "file:///C:/Documents%20and%20Settings/FileSchemeURIs.doc",
                ),
                (
                    r"\\?\UNC\laptop"
                    + long_path_string
                    + r"\Documents and Settings\FileSchemeURIs.doc",
                    f"file://laptop/{long_path_url_string}Documents%20and%20Settings/FileSchemeURIs.doc",
                ),
                (
                    r"\\?\C:" + long_path_string + r"\FileSchemeURIs.doc",
                    f"file:///C:{long_path_url_string}/FileSchemeURIs.doc",
                ),
            ),
        }

        current_type = PathType.kWindows if os.name == "nt" else PathType.kPOSIX
        expected_results[PathType.kSystem] = expected_results[current_type]

        for path, url in expected_results[path_type]:
            assert utils.pathToFileURL(path, path_type) == url
            assert utils.pathFromFileURL(url, path_type) == path


class Test_pathToFileURL:
    @pytest.mark.parametrize(
        "path_type", (PathType.kSystem, PathType.kPOSIX, PathType.kWindows)
    )
    def test_when_relative_path_then_InputValidataionException_raised(self, path_type):

        rel_paths = {
            PathType.kPOSIX: ("./some/path", "some/path"),
            PathType.kWindows: (r".\some\path", r"some\path", r"C:some\path")
        }

        current_type = PathType.kWindows if os.name == "nt" else PathType.kPOSIX
        rel_paths[PathType.kSystem] = rel_paths[current_type]

        for path in rel_paths[path_type]:
            with pytest.raises(InputValidationException) as exc:
                utils.pathToFileURL(path, path_type)
            assert str(exc.value) == f"pathToFileURL: Absolute paths required ({path})"


class Test_pathFromFileURL:
    @pytest.mark.parametrize(
        "path_type", (PathType.kSystem, PathType.kPOSIX, PathType.kWindows)
    )
    def test_when_not_file_scheme_then_InputValidataionException_raised(
        self, path_type
    ):
        url = "filethisisnot://somehost/some/path"
        with pytest.raises(InputValidationException) as exc:
            utils.pathFromFileURL(url, path_type)
        assert str(exc.value) == f"pathFromFileURL: Must be a 'file' scheme URL ({url})"

    def test_when_host_set_and_posix_path_type_then_InputValidataionException_raised(
        self,
    ):
        url = "file://somehost/some/path"
        with pytest.raises(InputValidationException) as exc:
            utils.pathFromFileURL(url, PathType.kPOSIX)
        assert (
            str(exc.value)
            == f"pathFromFileURL: Can't extract a POSIX path from a file URL with a host ({url})"
        )
