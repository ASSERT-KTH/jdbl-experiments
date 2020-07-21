#!/usr/bin/env python3

import os
import shutil
import json
import datetime
import argparse
import subprocess
import zipfile

import xml.etree.ElementTree as xml

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_file = os.path.join(os.path.dirname(
    __file__), '..', 'dataset', 'data', 'jdbl_dataset.json')

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)


def get_type(path):
    extension = path[path.rfind('.'):].lower()

    if '.class' == extension:
        return "class"
    if '.jpg' in extension or '.png' in extension or '.gif' in extension:
        return "image"
    if '.mp4' in extension or '.avi' == extension:
        return "video"
    if '.txt' in extension or '.md' == extension or '.mf' == extension or '.properties' == extension:
        return "text"
    if '.xml' in extension:
        return "xml"
    return 'other'


def get_zip_content(path):
    output = {}
    zip = zipfile.ZipFile(path)
    for f in zip.filelist:
        if f.filename[-1] == "/":
            continue
        output[f.filename] = {
            'path': f.filename,
            'type': get_type(f.filename),
            'size': f.file_size
        }
    return output


def get_debloat_report(path):
    output = {'bloated': [], 'preserved': [], 'method': []}
    if os.path.exists(os.path.join(path, 'debloat-report.csv')):
        with open(os.path.join(path, 'debloat-report.csv')) as fd:
            lines = fd.readlines()
            for l in lines:
                if len(l.split(",")) < 2:
                    continue
                if len(l.split(",")) < 2:
                    continue
                type = l.split(",")[0]
                class_name = l.split(",")[1].strip()
                if ":" in class_name:
                    class_name = class_name.split(":")[0]
                if type == "BloatedMethod":
                    output['method'].append(class_name)
                if type == "BloatedClass":
                    output['bloated'].append(class_name)
                elif type == "PreservedClass":
                    output['preserved'].append(class_name)
    return output


with open(PATH_file, 'r') as fd:
    data = json.load(fd)

    original_total = 0
    internal_total = 0
    debloat_total = 0
    method_total = 0
    preserved_total = 0
    resource_total = 0
    bytecode_total = 0

    content = 'lib,file.path,file.type,debloat.type,original.size,debloated.size\n'
    for lib_id in data:
        lib = data[lib_id]
        lib_id = lib['repo_name']
        lib_path = os.path.join(
            PATH_results, lib['repo_name'].replace('/', '_'))
        for version in lib['clients']:
            if version not in lib['releases']:
                continue
            version_path = os.path.join(lib_path, version)
            original_path = os.path.join(version_path, 'original')
            debloat_path = os.path.join(version_path, 'debloat')

            debloat_report = get_debloat_report(debloat_path)

            original_jar_path = os.path.join(original_path, 'original.jar')
            debloat_jar_path = os.path.join(debloat_path, 'debloat.jar')
            dup_jar_path = os.path.join(debloat_path, 'dup.jar')

            if not os.path.exists(original_jar_path) or not os.path.exists(debloat_jar_path):
                continue
            original_content = get_zip_content(original_jar_path)
            debloat_content = get_zip_content(debloat_jar_path)

            shutil.copyfile(original_jar_path, dup_jar_path)
            cl_2_remove = []
            cl_2_method = []

            for path in original_content:
                info = original_content[path]
                info_debloat = None
                debloat_size = 0
                type = "resource"
                if path in debloat_content:
                    debloat_size = debloat_content[path]['size']
                if '.class' in path:
                    type = "none"
                    class_name = path.replace(".class", '').replace("/", '.')
                    if class_name in debloat_report['bloated']:
                        debloat_total += info['size']
                        debloat_size = 0
                        type = "bloated"
                        cl_2_remove.append(path)
                    elif class_name in debloat_report['preserved']:
                        preserved_total += info['size']
                        type = "preserved"
                    elif class_name in debloat_report['method']:
                        method_total += info['size'] - debloat_size
                        cl_2_method.append(path)
                        type = "method"
                    if "$" in path:
                        internal_total += info['size']
                if type == "resource":
                    resource_total += info['size']
                else:
                    bytecode_total += info['size']
                original_total += info['size']
                content += (
                    f"{lib_id.replace('/', '_')}_{version},{path},{info['type']},{type},{info['size']},{debloat_size}\n")

            if len(cl_2_remove + cl_2_method) > 0:
                cmd = ['zip', '-d', dup_jar_path] + cl_2_remove + cl_2_method
                subprocess.check_call(" ".join(cmd).replace("$", "\$") + " > /dev/null", shell=True)
            if len(cl_2_method) > 0:
                with zipfile.ZipFile(debloat_jar_path) as zip:
                    with zipfile.ZipFile(dup_jar_path, 'a') as zipf:
                        for p in cl_2_method:
                            p = p.replace('"', '')
                            zipf.writestr(p, zip.read(p))
    with open("../jar_analysis.csv", 'w') as fdo:
        fdo.write(content)

    def print_latex_variable(name, value):
        print("\def\%s{%s}" % (name, value))

    print_latex_variable("totalSize", original_total)
    print_latex_variable("resourceSize", resource_total)
    print_latex_variable("bytcodeSize", bytecode_total)
    print_latex_variable("debloatedSize", debloat_total)
    print_latex_variable("debloatedMethodSize", method_total)
    print_latex_variable("preservedSize", preserved_total)

    print_latex_variable("internalTotal", internal_total)
    print(bytecode_total, debloat_total, (debloat_total)*100/bytecode_total)
