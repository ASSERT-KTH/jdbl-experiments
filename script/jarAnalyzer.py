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
with open(PATH_file, 'r') as fd:
    data = json.load(fd)

    content = 'lib,file.path,type,original.size,debloated.size\n'
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
            debloat_jar_path = os.path.join(debloat_path, 'debloat.jar')
            
            if not os.path.exists(original_jar_path) or not os.path.exists(debloat_jar_path):
                continue
            original_content = get_zip_content(original_jar_path)
            debloat_content = get_zip_content(debloat_jar_path)

            for path in original_content:
                info = original_content[path]
                info_debloat = None
                debloat_size = 0
                if path in debloat_content:
                    debloat_size = debloat_content[path]['size']
                content += (f"{lib_id.replace('/', '_')}_{version},{path},{info['type']},{info['size']},{debloat_size}\n")
    with open("../jar_analysis.csv", 'w') as fdo:
        fdo.write(content)
            
            

