#!/usr/bin/env python3

import argparse
import tempfile
import subprocess
import os
import sys
from core.JDBL import JDBL
from core.Project import Project
from core.Debloat import Debloat

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dependency", required=True,
                        help="The GitHub url of the debloated dependency")
    parser.add_argument(
        "--lib-commit", help="The commit of the lib to debloat")
    parser.add_argument('-c', "--client", required=True,
                        help="The GitHub url of the client")
    parser.add_argument("--client-commit",
                        help="The commit of the lib to debloat")
    parser.add_argument('-v', "--version", help="The version of the libray")
    parser.add_argument('--output', required=True, help="The output folder")

    args = parser.parse_args()

    working_directory = tempfile.mkdtemp()

    dep = Project(args.dependency)
    client = Project(args.client)

    result_path = os.path.join(
        args.output, dep.repo.replace('/', '_'), args.version)
    if not os.path.exists(result_path):
        print("exit", result_path, "does not exists")
        sys.exit(0)

    lib_debloat_path = os.path.join(result_path, "debloat")
    path_test_results = os.path.join(lib_debloat_path, "verify-test-results")
    if not os.path.exists(path_test_results):
        dep.clone(working_directory)
        dep.checkout_commit(args.lib_commit)

        debloat = Debloat(dep)
        debloat.inject_library()
        dep.inject_jacoco_plugin()
        dep.test()
        dep.copy_test_results(path_test_results)

    client_path_result = os.path.join(
        result_path, "clients", client.repo.replace('/', '_'), 'debloat')
    path_client_test_results = os.path.join(
        client_path_result, "verify-test-results")

    if not os.path.exists(path_client_test_results):
        if dep.pom is None:
            dep.clone(working_directory)
            dep.checkout_commit(args.lib_commit)
        client.clone(working_directory)
        client.checkout_commit(args.client_commit)
        client.inject_debloat_library(
            args.output, dep, args.version, debloated=False)
        client.unzip_debloat(args.output, dep, args.version, debloated=False)
        client.test()
        client.copy_test_results(path_client_test_results)
