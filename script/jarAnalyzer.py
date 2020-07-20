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
    debloat_total = 0

    content = 'lib,file.path,file.type,debloat.type,original.size,debloated.size\n'
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
            
            debloat_report = get_debloat_report(debloat_path)

            original_jar_path = os.path.join(original_path, 'original.jar')
            debloat_jar_path = os.path.join(debloat_path, 'debloat.jar')
            
            if not os.path.exists(original_jar_path) or not os.path.exists(debloat_jar_path):
                continue
            original_content = get_zip_content(original_jar_path)
            debloat_content = get_zip_content(debloat_jar_path)

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
                        debloat_size = 0
                        type = "bloated"
                    elif class_name in debloat_report['preserved']:
                        type = "preserved"
                    elif class_name in debloat_report['method']:
                        type = "method"
                original_total += info['size']
                debloat_total += debloat_size
                content += (f"{lib_id.replace('/', '_')}_{version},{path},{info['type']},{type},{info['size']},{debloat_size}\n")
    with open("../jar_analysis.csv", 'w') as fdo:
        fdo.write(content)
    print(original_total, debloat_total, (original_total-debloat_total)*100/original_total)
            
            

