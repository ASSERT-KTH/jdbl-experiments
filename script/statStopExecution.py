#!/usr/bin/env python3

import os
import json
import xml.etree.ElementTree as xml

PATH = os.path.join(os.path.dirname(__file__), 'results', 'executions')

def extractException(file):
    bufMode = False
    buf = ''
    errors = []
    with open(file, 'r') as f:
        for line in f:
            if bufMode:
                if not line.startswith(' '):
                    bufMode = False
            else:
                if 'Traceback' in line:
                    bufMode = True
                else:
                    continue
            # Truncate lines longer than 400 characters.
            if len(line) > 400:
                line = line[:400] + '...\n'
            buf += line
            if not bufMode:
                print(buf)
                errors.append(buf)
                buf = ''
    return set(errors)

steps = {}
total_time = 0
for f in os.listdir(PATH):
    if '.log' in f:
        extractException(os.path.join(PATH, f))
    if '.json' not in f:
        continue
    with open(os.path.join(PATH, f)) as fd:
        try:
            data = json.load(fd)
            total_time += data['end'] - data['start']
            for s in data['steps']:
                if 'success' not in s or  s['success'] == False:
                    name = s['name']
                    if name not in steps:
                        steps[name] = 0
                    steps[name] += 1
        except:
            print("%s is not a valid json" % f)
            continue
print(steps)
print("Total execution time", total_time)