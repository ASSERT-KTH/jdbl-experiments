#!/usr/bin/env python3
import os
import json
import argparse

from Results import results

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory",
                    default="/mnt/results3")

args = parser.parse_args()

PATH_file = os.path.join(os.path.dirname(
    __file__), '..', 'dataset', 'data', 'jdbl_dataset.json')

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)

def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))

counts = {}

def count(key, value):
    if key not in counts:
        counts[key] = {}
    if value not in counts[key]:
        counts[key][value] = 0
    counts[key][value] += 1


for lib in results.libs:
    lib_path = os.path.join(PATH_results, lib.id())
    for version in lib.versions:
        version_path = os.path.join(lib_path, version.version)
        
        debloat_path = os.path.join(version_path, 'debloat')
        debloat_log = os.path.join(debloat_path, 'execution.log')
        
        count('total', True)
        count('compile', version.compiled)
        count('debloat', version.debloat)
        count('error', version.compiled and not version.debloat)
        
        if version.compiled and not version.debloat and os.path.exists(debloat_log):
            last_step = "Initial tests"
            try:
                with open(debloat_log, 'r', encoding="utf-8") as fd:
                    content = fd.read()
                    if "JDBL: STARTING TEST BASED DEBLOAT" in content:
                        last_step = "JDBL start"
                        pass
                    if "se.kth.castor.jdbl.coverage.JCovCoverage  - Running JCov" in content:
                        last_step = "JCov"
                        pass
                    if "se.kth.castor.jdbl.coverage.JCovCoverage  - Generating JCov report" in content:
                        pass
                    if "se.kth.castor.jdbl.coverage.YajtaCoverage  - Running yajta" in content:
                        last_step = "yajta"
                        pass
                    if "se.kth.castor.jdbl.coverage.JacocoCoverage  - Running JaCoCo" in content:
                        last_step = "JaCoCo"
                        pass
                    if "se.kth.castor.jdbl.coverage.JacocoCoverage  - Analyzing" in content:
                        pass
                    if "se.kth.castor.jdbl.coverage.JVMClassCoverage  - Starting executing tests" in content:
                        last_step = "JVMClassCoverage"
                        pass
                    if "Loaded classes (" in content:
                        pass
                    if "[INFO] Starting removing unused classes..." in content:
                        last_step = "Remove classes"
                        pass
                    if "[INFO] Starting removing unused methods..." in content:
                        last_step = "Remove methods"
                        pass
                    if "[INFO] Starting running the test suite on the debloated version..." in content:
                        last_step = "Validation"
                        pass
                    if "JDBL: TEST BASED DEBLOAT FINISHED" in content:
                        last_step = "Done"
                        pass
                    last_line = content.split("\n")[-2]
                    crash = (
                        last_line == "[INFO] Build failures were ignored." or "xception" in last_line or "Thread.java" in last_line) and last_step != 'Done'
                    count('crash', crash)
                    count('last_step', last_step)
                print(lib.repo, version.version, last_step, crash, last_line)
            except Exception as e:
                print(lib.repo, version.version, e)
                pass

print(counts)

macro("nbLibDebSuccessNum", counts['debloat'][True])
macro("nbLibNotCompile", counts['compile'][False])
macro("nbLibCrash", counts['crash'][True] if True in counts['crash'] else 0)
macro("nbLibTimeout", counts['crash'][False] - counts['last_step']['Done'])
macro("nbLibValidation", counts['last_step']['Done'])