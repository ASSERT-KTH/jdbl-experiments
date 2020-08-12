#!/usr/bin/env python3

import os
import json
import datetime
import statistics

from Results import results

def str_num(num, unit=None):
    if unit is None:
        return f"\\np{{{num}}}"
    elif unit == "%":
        return f"\\np[\%]{{{round(num*100, 1)}}}"
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
macro("nbTestClient", sum(nb_test_client))
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

print(f"\# Tests & {str_num(min(nb_test))} & {str_num(nb_test_quantiles[0])} & {str_num(nb_test_quantiles[1])} & {str_num(nb_test_quantiles[2])} & {str_num(max(nb_test))} & {str_num(statistics.mean(nb_test))} & \\nbTestStr \\\\")
print(f"\# Loc   & {str_num(min(nb_line_lib))} & {str_num(nb_line_lib_quantiles[0])} & {str_num(nb_line_lib_quantiles[1])} & {str_num(nb_line_lib_quantiles[2])} & {str_num(max(nb_line_lib))} & {str_num(statistics.mean(nb_line_lib))} & \\nbLineLibStr \\\\")
print(f"Coverage & {str_num(min(coverage_lib), unit='%')} & {str_num(coverage_lib_quantiles[0], unit='%')} & {str_num(coverage_lib_quantiles[1], unit='%')} & {str_num(coverage_lib_quantiles[2], unit='%')} & {str_num(max(coverage_lib), unit='%')} & {str_num(statistics.mean(coverage_lib), unit='%')} & N.A \\\\")


nb_test_client_quantiles = statistics.quantiles(nb_test_client, n=4)
nb_line_client_quantiles= statistics.quantiles(nb_line_client, n=4)
coverage_client_quantiles= statistics.quantiles(coverage_client, n=4)

print(f"\# Tests & {str_num(min(nb_test_client))} & {str_num(nb_test_client_quantiles[0])} & {str_num(nb_test_client_quantiles[1])} & {str_num(nb_test_client_quantiles[2])} & {str_num(max(nb_test_client))} & {str_num(statistics.mean(nb_test_client))} & \\nbTestStr \\\\")
print(f"\# Loc   & {str_num(min(nb_line_client))} & {str_num(nb_line_client_quantiles[0])} & {str_num(nb_line_client_quantiles[1])} & {str_num(nb_line_client_quantiles[2])} & {str_num(max(nb_line_client))} & {str_num(statistics.mean(nb_line_client))} & \\nbLineLibStr \\\\")
print(f"Coverage & {str_num(min(coverage_client), unit='%')} & {str_num(coverage_client_quantiles[0], unit='%')} & {str_num(coverage_client_quantiles[1], unit='%')} & {str_num(coverage_client_quantiles[2], unit='%')} & {str_num(max(coverage_client), unit='%')} & {str_num(statistics.mean(coverage_client), unit='%')} & N.A \\\\")