#!/usr/bin/env python3

import os, shutil
import json
import datetime
import argparse
import subprocess
import zipfile

import xml.etree.ElementTree as xml

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'data', 'jdbl_dataset.json')

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)


with open(PATH_file, 'r') as fd:
    data = json.load(fd)
    for lib_id in data:
        lib = data[lib_id]
        lib_id = lib['repo_name']
        lib_path = os.path.join(PATH_results, lib['repo_name'].replace('/', '_'))
        for version in lib['clients']:
            if version not in lib['releases']:
                continue
            version_path = os.path.join(lib_path, version)
            original_path = os.path.join(version_path, 'original')
            debloat_path = os.path.join(version_path, 'debloat') 
            
            original_jar_path = os.path.join(original_path, 'original.jar')
            
            if not os.path.exists(original_jar_path):
                continue

            cl_2_remove = []
            if os.path.exists(os.path.join(debloat_path, 'debloat-report.csv')):
                with open(os.path.join(debloat_path, 'debloat-report.csv')) as fd:
                    lines = fd.readlines()
                    for l in lines:
                        if len(l.split(",")) < 2:
                            continue
                        (type, cl, o_type) = l.split(",")
                        if "BloatedClass" == type:
                            cl_2_remove.append(cl.replace(".", "/") + ".class")
            if len(cl_2_remove) > 0:
                dup_jar_path = os.path.join(debloat_path, 'dup.jar')
                shutil.copyfile(original_jar_path, dup_jar_path)
                cmd=['zip', '-d', dup_jar_path] + cl_2_remove
                subprocess.check_call(cmd)

                print(os.stat(dup_jar_path).st_size, os.stat(original_jar_path).st_size)

