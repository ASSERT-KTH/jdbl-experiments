#!/usr/bin/env python3

import os
import json
import argparse
import xml.etree.ElementTree as xml

from Results import results

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)


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

        
        print(version.nb_class, dep_classes)
        nb_classes += version.nb_class
        nb_method += version.nb_method

        nb_bloated_classes += version.nb_debloat_class
        nb_bloated_method += version.nb_debloat_method
        

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
