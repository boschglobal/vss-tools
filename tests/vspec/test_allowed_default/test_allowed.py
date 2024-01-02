#!/usr/bin/env python3

# Copyright (c) 2023 Contributors to COVESA
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License 2.0 which is available at
# https://www.mozilla.org/en-US/MPL/2.0/
#
# SPDX-License-Identifier: MPL-2.0

import pytest
import os


@pytest.fixture
def change_test_dir(request, monkeypatch):
    # To make sure we run from test directory
    monkeypatch.chdir(request.fspath.dirname)


def run_exporter(exporter, argument):
    test_str = "../../../vspec2" + exporter + ".py " + argument + " test.vspec out." + exporter + " > out.txt 2>&1"
    result = os.system(test_str)
    assert os.WIFEXITED(result)
    assert os.WEXITSTATUS(result) == 0
    test_str = "diff out." + exporter + " expected." + exporter
    result = os.system(test_str)
    assert os.WIFEXITED(result)
    assert os.WEXITSTATUS(result) == 0

    # Check if warning given
    # ddsidl can not handle float and integer
    # Some other tools ignore "allowed" all together
    if exporter in ["ddsidl"]:
        expected_grep_result = 0
    else:
        expected_grep_result = 1

    test_str = 'grep \"can only handle allowed values for string type\" out.txt > /dev/null'
    result = os.system(test_str)
    assert os.WIFEXITED(result)
    assert os.WEXITSTATUS(result) == expected_grep_result
    os.system("rm -f out." + exporter + " out.txt")


def test_allowed(change_test_dir):

    # Run all "supported" exporters, i.e. not those in contrib
    # Exception is "binary", as it is assumed output may vary depending on target
    exporters = ["json", "ddsidl", "csv", "yaml", "franca", "graphql"]
    for exporter in exporters:
        run_exporter(exporter, "-u ../test_units.yaml")


@pytest.mark.parametrize("file", [
    "test_not_only_uppercase_1.vspec",
    "test_not_only_uppercase_2.vspec",
    "test_not_only_uppercase_3.vspec",
    ])
def test_warning(file, change_test_dir):
    """
    Files that are legal VSS but should not pass in strict mode.
    Strict mode intended to be used for standard catalog
    """

    extra_args = ["", "-s", "--strict", "--abort-on-name-style"]

    for extra_arg in extra_args:

        test_str = "../../../vspec2json.py -u ../test_units.yaml " + extra_arg + " " + file + " out.json > out.txt 2>&1"
        result = os.system(test_str)
        assert os.WIFEXITED(result)
        if extra_arg == "":
            assert os.WEXITSTATUS(result) == 0
        else:
            assert os.WEXITSTATUS(result) != 0

        test_str = 'grep \"is not following naming conventions\" out.txt > /dev/null'
        result = os.system(test_str)
        assert os.WIFEXITED(result)
        assert os.WEXITSTATUS(result) == 0

        test_str = 'grep \"You asked for strict checking. Terminating\" out.txt > /dev/null'
        result = os.system(test_str)
        assert os.WIFEXITED(result)
        if extra_arg == "":
            assert os.WEXITSTATUS(result) != 0
        else:
            assert os.WEXITSTATUS(result) == 0

        os.system("rm -f out.json out.txt")


@pytest.mark.parametrize(("file", "grep_string"), [
    ("test_numeric_on_bool.vspec", "is not"),
    ("test_numeric_on_string.vspec", "is not"),
    ("test_string_on_numeric.vspec", "is not"),
    ("test_numeric_on_bool_default.vspec", "is not"),
    ("test_numeric_on_string_default.vspec", "is not"),
    ("test_string_on_numeric_default.vspec", "is not"),
    ("test_not_array.vspec", "Allowed values are not represented as array"),
    ("test_default_not_allowed_string.vspec", "not listed as allowed value"),
    ("test_default_not_allowed_float.vspec", "not listed as allowed value"),
    ("test_default_not_allowed_int.vspec", "not listed as allowed value"),
    ])
def test_error(file, grep_string, change_test_dir):
    """
    Files that are not legal VSS
    Strict mode intended to be used for standard catalog
    """

    test_str = "../../../vspec2json.py -u ../test_units.yaml " + file + " out.json > out.txt 2>&1"
    result = os.system(test_str)
    assert os.WIFEXITED(result)
    assert os.WEXITSTATUS(result) != 0

    # Actual message varies a bit
    test_str = 'grep \"' + grep_string + '\" out.txt > /dev/null'
    result = os.system(test_str)
    assert os.WIFEXITED(result)
    assert os.WEXITSTATUS(result) == 0

    os.system("rm -f out.json out.txt")
