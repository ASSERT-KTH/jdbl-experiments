#!/usr/bin/env python3

import os
import json
import datetime
import statistics

from Results import results

def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))
    if not isinstance(value, str):
        print("\\def\\%sStr{\\np{\\%s}\\xspace}" % (name, name))

nb_lib_version = 0
nb_lib_compiling = 0
nb_lib_debloat = 0
nb_no_clients = 0
nb_client = 0
nb_all_client = 0
nb_validated_debloated_client = 0
nb_invalidated_debloated_client = 0
nb_fail_debloat_client = 0
nb_test = 0
nb_test_client = 0
nb_failing_debloated_test = 0
execution_time = 0
debloat_time = 0
nb_line_lib = 0
nb_line_client = 0

coverage_lib = []
coverage_client = []

for lib in results.libs:
    for version in lib.versions:
        nb_lib_version += 1
        if version.compiled:
            nb_lib_compiling += 1
        if version.debloat:
            nb_lib_debloat += 1
            if len(version.clients) == 0:
                nb_no_clients += 1
        if version.debloat_time:
            debloat_time += version.debloat_time
        if version.coverage is not None:
            nb_line_lib += version.coverage.nb_lines
            coverage_lib.append(version.coverage.coverage)
        if version.original_test is not None:
            nb_test += version.original_test.nb_test()

        for c in version.clients:
            nb_all_client += 1
            execution_time += c.execution_time
            if c.original_test is not None:
                nb_client += 1
                nb_test_client += c.original_test.nb_test()
                if c.debloat_test is not None:
                    if c.original_test.passing == c.debloat_test.passing:
                        nb_validated_debloated_client += 1
                    else:
                        nb_invalidated_debloated_client += 1
                    nb_failing_debloated_test += max(c.original_test.passing - c.debloat_test.passing, 0)
                else:
                    nb_fail_debloat_client += 1
            if c.coverage_original is not None:
                nb_line_client += c.coverage_original.nb_lines
                coverage_client.append(c.coverage_original.coverage)

macro("nbLib", len(results.libs))
macro("nbLibVersion", nb_lib_version)
macro("nbLibCompiling", nb_lib_compiling)
macro("nbLibDebloat", nb_lib_debloat)
macro("nbTest", nb_test)
macro("nbTestClient", nb_test_client)
macro("nbFailingDebloatedTest", nb_failing_debloated_test)
macro("nbClientAll", nb_all_client)
macro("nbClient", nb_client)
macro("nbFailDebloatClient", nb_fail_debloat_client)
macro("nbValidatedDebloatedClient", nb_validated_debloated_client)
macro("nbInvalidatedDebloatedClient", nb_invalidated_debloated_client)

if len(coverage_lib) > 0:
    macro("meanCoverageLib", round(statistics.mean(coverage_lib) * 100, 2))
    macro("medianCoverageLib", round(statistics.median(coverage_lib) * 100, 2))
if len(coverage_client) > 0:
    macro("meanCoverageClient", round(statistics.mean(coverage_client) * 100, 2))
    macro("medianCoverageClient", round(statistics.median(coverage_client) * 100, 2))

macro("nbLineLib", nb_line_lib)
macro("nbLineClient", nb_line_client)

macro("executionTime", str(datetime.timedelta(seconds=int(execution_time))))
macro("debloatTime", str(datetime.timedelta(seconds=float(debloat_time))))
