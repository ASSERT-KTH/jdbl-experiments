#!/usr/bin/env python3

import os
import json
import argparse
import xml.etree.ElementTree as xml

from Results import results

PATH_results = os.path.join(os.path.dirname(__file__), 'results')


def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))


def clean_exception(name):
    name = name.replace(":", "").strip()
    if "junit" in name or "Assertion" in name:
        return "Assert"
    return os.path.basename(name.replace(".", "/"))


def extract_error_type(e):
    exception = clean_exception(e.attrib['type'])
    if 'message' not in e.attrib:
        return exception
    message = e.attrib['message'].strip()
    if "java.lang.UnsupportedOperationException" in message:
        exception = clean_exception("java.lang.UnsupportedOperationException")
    elif " not found" in message:
        exception = clean_exception("NoClassDefFoundError")
    elif "NoClassDefFoundError" in message:
        exception = clean_exception("NoClassDefFoundError")
    elif "timed out" in message:
        exception = "TimeoutException"
    elif "org.springframework.beans.factory.BeanCreationException:" in message:
        exception = "BeanCreationException"
    elif "but was<java.lang.AssertionError>" in message:
        exception = "AssertionError"
    else:
        #print(e.attrib, exception)
        pass
    return exception


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
            raise e
            pass
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="The output directory")

    args = parser.parse_args()

    if args.output:
        PATH_results = os.path.abspath(args.output)

    total = 0
    nb_lib_pass_test = 0
    not_executed = 0
    nb_different_number_test = 0
    nb_failing_test = 0
    nb_passing_test = 0
    total_test = 0
    total_test_for_passing = 0
    nb_failing = 0
    nb_error = 0
    errors = {}

    failing_libs = []

    for lib in results.libs:
        lib_path = os.path.join(PATH_results, lib.id())
        for version in lib.versions:
            version_path = os.path.join(lib_path, version.version)
            if not version.compiled or not version.debloat:
                continue
            total += 1
            if version.original_test is None or version.debloat_test is None:
                not_executed += 1
                continue
            if version.original_test.nb_test() != version.original_test.passing:
                not_executed += 1
                continue
            debloat_path = os.path.join(version_path, "debloat")

            nb_test = version.original_test.nb_test()
            nb_debloat_test = version.debloat_test.nb_test()
            if nb_test != nb_debloat_test:
                nb_different_number_test += 1
                continue
            total_test += nb_debloat_test
            if version.debloat_test.error + version.debloat_test.failing != 0:
                nb_failing += 1
                nb_error += version.debloat_test.error
                nb_failing_test += version.debloat_test.error + version.debloat_test.failing
                failing_libs.append((version, get_error_message(debloat_path)))
            else:
                nb_lib_pass_test += 1
                total_test_for_passing += nb_test

    macro("nbLibDebSuccessNum", total)
    macro("nbLibPassTestNum", nb_lib_pass_test)
    macro("nbLibExcludedForTest", nb_different_number_test + not_executed)
    macro("nbLibTestFailing", nb_failing)
    macro("nbUniqueTestNum", total_test)
    macro("nbTestForPassingNum", total_test_for_passing)
    macro("nbFailingTest", nb_failing_test)
    macro("nbErrorTest", nb_error)

    total_taf = 0
    total_uoe = 0
    total_npe = 0
    total_tt = 0
    total_NCDF = 0
    total_IE = 0
    total_other = 0

    total_test = 0
    for (version, messages) in sorted(failing_libs, key=lambda x: (x[0].debloat_test.error + x[0].debloat_test.failing)/x[0].debloat_test.nb_test(), reverse=True):
        errors = {}

        taf = 0
        uoe = 0
        npe = 0
        tt = 0
        NCDF = 0
        IE = 0
        other = 0

        for e in messages:
            if e not in errors:
                errors[e] = 0
            errors[e] += 1
            if e == "Assert":
                taf += 1
                total_taf += 1
            elif e == "UnsupportedOperationException":
                uoe += 1
                total_uoe += 1
            elif e == "NullPointerException":
                npe += 1
                total_npe += 1
            elif e == "TimeoutException":
                tt += 1
                total_tt += 1
            elif e == "NoClassDefFoundError":
                NCDF += 1
                total_NCDF += 1
            else:
                other += 1
                total_other += 1

        if taf == 0:
            taf = ' '
        if uoe == 0:
            uoe = ' '
        if npe == 0:
            npe = ' '
        if tt == 0:
            tt = ' '
        if NCDF == 0:
            NCDF = ' '
        if IE == 0:
            IE = ' '
        if other == 0:
            other = ' '

        total_test += version.debloat_test.nb_test()
        name = version.library.repo.split("/")[1]
        print(
            f"{name}:{version.version} & {taf} & {uoe} & {npe} & {NCDF} & {other} & \ChartSmall[r]{{{len(messages)}}}{{{version.debloat_test.nb_test()}}} \\\\")
    print("\midrule")
    print(f"Total & {total_taf} & {total_uoe} & {total_npe} & {total_NCDF} & {total_other} & \ChartSmall{{\\nbFailingTest}}{{{total_test}}} \\\\")
