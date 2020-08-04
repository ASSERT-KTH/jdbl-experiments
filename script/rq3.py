#!/usr/bin/env python3

import os
import json
import argparse
import subprocess
import re
import xml.etree.ElementTree as xml

from Results import results

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)


def analyze_jar(jar_path):
    class_output = subprocess.check_output(
        ['jar', 'tf', jar_path]).decode("utf-8")
    classes = [c.replace('/', '.')
               for c in re.findall(r'(.*)\.class', class_output)]
    methods = []
    if classes:
        def_out = subprocess.check_output(
            ['javap', '-classpath', jar_path] + classes).decode("utf-8")
        # This is pretty hacky: look for parentheses in the declaration line.
        num_methods = sum(1 for line in def_out if '(' in line)
    else:
        num_methods = 0
    return (len(classes), num_methods)


def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))


total = 0
nb_lib_with_dependencies = 0

nb_dependencies = 0
nb_classes = 0
nb_method = 0

nb_bloated_dependencies = 0
nb_bloated_classes = 0
nb_bloated_method = 0

count_bloated_class_dependencies = 0
count_bloated_preserved_dependencies = 0
count_class_dependencies = 0
count_method_dependencies = 0
count_bloated_method_dependencies = 0

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

        total += 1

        dep_classes = 0

        original_path = os.path.join(version_path, 'original')
        debloat_path = os.path.join(version_path, 'debloat')
        original_jar_path = os.path.join(original_path, 'original.jar')
        debloat_jar_path = os.path.join(debloat_path, 'debloat.jar')

        original_stat = analyze_jar(original_jar_path)
        debloat_stat = analyze_jar(debloat_jar_path)

        if len(version.dependencies) > 0:
            nb_lib_with_dependencies += 1
        for dependency in version.dependencies:
            nb_dependencies += 1

            if dependency.nb_class == dependency.nb_debloat_class + dependency.nb_preserved_class:
                nb_bloated_dependencies += 1
            dep_classes += dependency.nb_class
            count_bloated_class_dependencies += dependency.nb_debloat_class
            count_bloated_preserved_dependencies += dependency.nb_preserved_class
            count_class_dependencies += dependency.nb_class
            count_method_dependencies += dependency.nb_method
            count_bloated_method_dependencies += dependency.nb_debloat_method

        nb_classes += original_stat[0]
        nb_method += original_stat[1]

        nb_bloated_classes += original_stat[0] - debloat_stat[0]
        nb_bloated_method += original_stat[1] - debloat_stat[1]


macro("Total", total)
macro("nbLibWithDependencies", nb_lib_with_dependencies)
macro("nbDependencies", nb_dependencies)
macro("nbClasses", nb_classes)
macro("nbMethods", nb_method)
macro("nbBloatedDependencies", nb_bloated_dependencies)
macro("nbBloatedClasses", nb_bloated_classes)
macro("nbBloatedMethods", nb_bloated_method)

macro("nbDepClasses", count_class_dependencies)
macro("nbDepMethods", count_method_dependencies)
macro("nbBloatedDepClasses", count_bloated_class_dependencies)
macro("nbPreservedDepClasses", count_bloated_preserved_dependencies)
macro("nbBloatedDepMethods", count_bloated_method_dependencies)
