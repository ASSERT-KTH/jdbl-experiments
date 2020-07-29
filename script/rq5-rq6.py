#!/usr/bin/env python3

import os
import json
import argparse
import re
import xml.etree.ElementTree as xml

from Results import results
from rq2 import extract_error_type

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)


def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))


def get_error_message(path):
    output = []
    test_results_path = os.path.join(path, "test-results")
    if not os.path.exists(test_results_path):
        return output
    for test in os.listdir(test_results_path):
        if ".xml" not in test:
            continue
        test_path = os.path.join(test_results_path, test)
        try:
            test_results = xml.parse(test_path).getroot()
            errors = test_results.findall("*/error")
            for e in errors:
                output.append(extract_error_type(e))
            errors = test_results.findall("*/failure")
            for e in errors:
                output.append(extract_error_type(e))
        except Exception as e:
            print(e)
            pass
    return output


def get_preserved_classes(debloat_path):
    output = []
    if os.path.exists(os.path.join(debloat_path, 'debloat-report.csv')):
        with open(os.path.join(debloat_path, 'debloat-report.csv'), 'r', encoding="utf-8") as fd:
            lines = fd.readlines()
            for l in lines:
                (bloat, class_name, type) = l.strip().split(',')
                if "PreservedClass" == bloat:
                    output.append(class_name)
    return output

compilation_errors_regex = [
    r"\[ERROR\] (.+):\[(\d+),(\d+)\] (.+)\n(.+)"
]
def extract_compilation_errors(debloat_log_path):
    output = []
    with open(debloat_log_path, 'r', encoding="utf-8") as lfd:
        try:
            content = lfd.read()
            matches = []
            for r in compilation_errors_regex:
                matches += re.findall(r, content)
            for (file, line, column, message, next_line) in matches:
                if "[deprecation]" in message:
                    message = "Deprecated method"
                    continue
                elif "package" in message and "does not exist" in message:
                    message = "package X does not exist"
                elif "cannot access " in message:
                    message = "cannot access X"
                elif "cannot find symbol" in message:
                    if " variable" in next_line:
                        next_line = "variable X"
                    elif " class" in next_line:
                        next_line = "class X"
                    elif " method" in next_line:
                        next_line = "method X"
                    else:
                        next_line = "other"
                    message = "cannot find symbol " + next_line
                output.append(message)
            if len(output) == 0:
                if "java.lang.UnsupportedOperationException" in content:
                    output.append("UnsupportedOperationException")
                elif "No tests to run." in content:
                    pass
                elif "Some Enforcer rules have failed." in content:
                    output.append("Plugin verification")
            #print(content)
        except Exception as e:
            print(debloat_log_path, e)
    return output

total = 0
compilation_error = 0
nb_preserved_client = 0
nb_preserved_considered = 0
other_error = 0
debloat_total = 0
debloat_error = 0
nb_lib_covered = 0
nb_static_usage = 0
plugin_error = 0

total_compilation_error = 0

nb_different_number_test = 0
nb_failing_test = 0
nb_total_test = 0
nb_failing = 0
no_log = 0
errors = {}
project_errors = {}
client_errors = {}
failing_versions = set()

compilation_errors = {}
project_compilation_errors = {}
client_compilation_errors = {}
failing_compilation_versions = set()
failing_compilation_clients = set()

for lib in results.libs:
    lib_path = os.path.join(PATH_results, lib.id())
    for version in lib.versions:
        version_path = os.path.join(lib_path, version.version)
        if not version.compiled or not version.debloat:
            continue
        if version.original_test is None or version.debloat_test is None:
            continue

        nb_test = version.original_test.nb_test()
        nb_debloat_test = version.debloat_test.nb_test()
        if nb_test != version.original_test.passing:
            continue
        if nb_test != nb_debloat_test or version.debloat_test.passing != nb_debloat_test:
            continue
        
        debloat_path = os.path.join(version_path, "debloat")
        preserved_classes = get_preserved_classes(debloat_path)
        for client in version.clients:
            client_path = os.path.join(version_path, "clients", client.id())
            client_debloat_path = os.path.join(client_path, 'debloat')
            if not os.path.exists(client_debloat_path):
                continue
            if not client.compiled:
                continue
            total += 1

            if not client.test_cover_lib and not client.static_use:
                continue
            debloat_total += 1
            if client.static_use:
                nb_static_usage += 1
                usage_path = os.path.join(os.path.dirname(
                    __file__), 'usageAnalysis', client.id() + ".csv")

                if os.path.exists(usage_path):
                    nb_preserved_considered += 1
                    with open(usage_path, 'r', encoding="utf-8") as ufd:
                        c = ufd.read()
                        for cl in preserved_classes:
                            if cl in c:
                                nb_preserved_client += 1
                if client.debloat_test is None:
                    debloat_error += 1
                    debloat_log_path = os.path.join(
                        client_debloat_path, 'execution.log')
                    if not os.path.exists(debloat_log_path):
                        other_error += 1
                        continue
                    ce = extract_compilation_errors(debloat_log_path)
                    if len(ce) == 0:
                        print("Empty error", lib.repo, client)
                    for e in ce:
                        if e not in compilation_errors:
                            compilation_errors[e] = 0
                            project_compilation_errors[e] = set()
                            client_compilation_errors[e] = set()
                            
                        total_compilation_error += 1
                        compilation_errors[e] += 1
                        project_compilation_errors[e].add(version)
                        client_compilation_errors[e].add(client)
                        failing_compilation_versions.add(version)
                        failing_compilation_clients.add(client)
                    with open(debloat_log_path, 'r', encoding="utf-8") as lfd:
                        try:
                            content = lfd.read()
                            if 'No tests to run.' in content:
                                debloat_error -= 1
                                continue
                            elif 'Compilation failure' in content:
                                compilation_error += 1
                            elif 'Fatal error compiling' in content:
                                compilation_error += 1
                            elif 'findbugs-maven-plugin' in content:
                                plugin_error += 1
                            elif 'spotbugs-maven-plugin' in content:
                                plugin_error += 1
                            elif 'maven-enforcer-plugin' in content:
                                plugin_error += 1
                            elif 'Found duplicate classes/resources!' in content:
                                plugin_error += 1
                            else:
                                other_error += 1
                                # print(content)
                        except Exception as e:
                            print(debloat_log_path, e)
            if client.test_cover_lib and client.debloat_test is not None:
                nb_test = client.original_test.nb_test()
                nb_debloat_test = client.debloat_test.nb_test()
                if nb_test != client.original_test.passing:
                    continue
                if nb_test != nb_debloat_test:
                    nb_different_number_test += 1
                    continue
                if client.test_cover_lib:
                    nb_lib_covered += 1
                nb_total_test += nb_test
                if client.debloat_test.passing != client.original_test.passing:
                    nb_failing += client.debloat_test.error + client.debloat_test.failing
                    failing_versions.add(version)
                    for e in get_error_message(os.path.join(client_path, 'debloat')):
                        if e not in errors:
                            errors[e] = 0
                            project_errors[e] = set()
                            client_errors[e] = set()
                        errors[e] += 1
                        project_errors[e].add(version)
                        client_errors[e].add(client)
                    nb_failing_test += 1

print("no_log", no_log)
macro("nbClient", total)
macro("nbCoveringClient", debloat_total)
macro("nbDynCoveringClient", nb_lib_covered)
macro("nbStatCoveringClient", nb_static_usage)
macro("nbDifferentNbtest", nb_different_number_test)
macro("nbFailingTestClient", nb_failing_test)
macro("nbFailingTestProject", len(failing_versions))
macro("nbClientTest", nb_total_test)
macro("nbClientFailure", nb_failing)
macro("nbClientDebloatError", debloat_error)
macro("nbClientDebloatCompilationError", compilation_error)
macro("nbClientDebloatPluginError", plugin_error)
macro("nbClientDebloatOtherError", other_error)
macro("nbClientConsideredPreserved", nb_preserved_considered)
macro("nbClientWithPreserved", nb_preserved_client)

print("\n\n% RQ5\n")

for (error, number) in sorted(compilation_errors.items(), key=lambda x: x[1], reverse=True):
    nb_project = len(project_compilation_errors[error])
    nb_client = len(client_compilation_errors[error])
    print("%s & \\ChartSmall{%s}{%s} & \\ChartSmall{%s}{%s} & \\ChartSmall{%s}{%s} \\\\" % (error, nb_project, len(failing_compilation_versions), nb_client, len(failing_compilation_clients), number, total_compilation_error))
print("\\midrule")
print(f"\\np{{{len(errors)}}} Errors & \\np{{{len(failing_compilation_versions)}}} Projects & \\np{{{len(failing_compilation_clients)}}} Clients & \\np{{{total_compilation_error}}} Compilation errors \\\\")

print("\n\n% RQ6\n")
for (error, number) in sorted(errors.items(), key=lambda x: x[1], reverse=True):
    nb_project = len(project_errors[error])
    nb_client = len(client_errors[error])
    print("%s & \\ChartSmall{%s}{\\nbFailingTestProject} & \\ChartSmall{%s}{\\nbFailingTestClient} & \\ChartSmall{%s}{%s} \\\\" % (error, nb_project, nb_client, number, "\\nbClientFailure"))
print("\\midrule")
print(f"\\np{{{len(errors)}}} Exceptions & \\np{{\\nbFailingTestProject}} Projects & \\np{{\\nbFailingTestClient}} Clients & \\np{{\\nbClientFailure}} Failing tests \\\\")
