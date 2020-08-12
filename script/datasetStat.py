#!/usr/bin/env python3

import os
import json
import datetime
import statistics

from Results import results

def macro(name, value, unit=None):
    print("\\def\\%s{%s}" % (name, value))
    if not isinstance(value, str):
        if unit is None:
            print("\\def\\%sStr{\\np{\\%s}\\xspace}" % (name, name))
        else:
            print("\\def\\%sStr{\\np[%s]{\\%s}\\xspace}" % (name, unit, name))

nb_lib_version = 0
nb_lib_compiling = 0
nb_client = 0
nb_all_client = 0
nb_test = []
nb_test_client = []
execution_time_lib = []
execution_time_client = []
debloat_time = []
nb_line_lib = []
nb_line_client = []

coverage_lib = []
coverage_client = []

for lib in results.libs:
    for version in lib.versions:
        nb_lib_version += 1
        if version.compiled:
            nb_lib_compiling += 1
        if version.debloat_time:
            debloat_time.append(version.debloat_time)
        if version.coverage is not None:
            nb_line_lib.append(version.coverage.nb_lines)
            coverage_lib.append(version.coverage.coverage)
        if version.original_test is not None:
            nb_test.append(version.original_test.nb_test())

        execution_time_lib.append(version.debloat_execution_time + version.original_execution_time)

        for c in version.clients:
            nb_all_client += 1
            if c.original_test is not None:
                nb_client += 1
                execution_time_client.append(c.debloat_execution_time + c.original_execution_time)
                nb_test_client.append(c.original_test.nb_test())
            if c.coverage_original is not None:
                nb_line_client.append(c.coverage_original.nb_lines)
                coverage_client.append(c.coverage_original.coverage)

macro("nbLib", len(results.libs))
macro("nbLibVersion", nb_lib_version)
macro("nbLibCompiling", nb_lib_compiling)
macro("nbTest", sum(nb_test))
macro("nbTestClient", nb_test_client)
macro("nbClientAll", nb_all_client)

if len(coverage_lib) > 0:
    macro("meanCoverageLib", round(statistics.mean(coverage_lib) * 100, 2), unit="\%")
    macro("medianCoverageLib", round(statistics.median(coverage_lib) * 100, 2), unit="\%")
if len(coverage_client) > 0:
    macro("meanCoverageClient", round(statistics.mean(coverage_client) * 100, 2), unit="\%")
    macro("medianCoverageClient", round(statistics.median(coverage_client) * 100, 2), unit="\%")

macro("nbLineLib", sum(nb_line_lib))
macro("nbLineClient", sum(nb_line_client))

macro("executionTimeLib", str(datetime.timedelta(seconds=float(sum(execution_time_lib)))))
macro("executionTimeClient", str(datetime.timedelta(seconds=float(sum(execution_time_client)))))
macro("executionTime", str(datetime.timedelta(seconds=float(sum(execution_time_client + execution_time_lib)))))
macro("debloatTime", str(datetime.timedelta(seconds=float(sum(debloat_time)))))


nb_test_quantiles = statistics.quantiles(nb_test, n=4)
nb_line_lib_quantiles= statistics.quantiles(nb_line_lib, n=4)
coverage_lib_quantiles= statistics.quantiles(coverage_lib, n=4)

print(f"\# Tests & {min(nb_test)} & {nb_test_quantiles[0]} & {nb_test_quantiles[1]} & {nb_test_quantiles[2]} & {max(nb_test)} & {statistics.mean(nb_test)} & \\nbTest \\\\")
print(f"\# Loc   & {min(nb_line_lib)} & {nb_line_lib_quantiles[0]} & {nb_line_lib_quantiles[1]} & {nb_line_lib_quantiles[2]} & {max(nb_line_lib)} & {statistics.mean(nb_line_lib)} & \\nbLineLib \\\\")
print(f"Coverage & {min(coverage_lib)} & {coverage_lib_quantiles[0]} & {coverage_lib_quantiles[1]} & {coverage_lib_quantiles[2]} & {max(coverage_lib)} & {statistics.mean(coverage_lib)} & N.A \\\\")


nb_test_client_quantiles = statistics.quantiles(nb_test_client, n=4)
nb_line_client_quantiles= statistics.quantiles(nb_line_client, n=4)
coverage_client_quantiles= statistics.quantiles(coverage_client, n=4)

print(f"\# Tests & {min(nb_test_client)} & {nb_test_client_quantiles[0]} & {nb_test_client_quantiles[1]} & {nb_test_client_quantiles[2]} & {max(nb_test_client)} & {statistics.mean(nb_test_client)} & \\nbTestClient \\\\")
print(f"\# Loc   & {min(nb_line_client)} & {nb_line_client_quantiles[0]} & {nb_line_client_quantiles[1]} & {nb_line_client_quantiles[2]} & {max(nb_line_client)} & {statistics.mean(nb_line_client)} & \\nbLineClient \\\\")
print(f"Coverage & {min(coverage_client)} & {coverage_client_quantiles[0]} & {coverage_client_quantiles[1]} & {coverage_client_quantiles[2]} & {max(coverage_client)} & {statistics.mean(coverage_client)} & N.A \\\\")
