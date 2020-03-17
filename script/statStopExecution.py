#!/usr/bin/env python3

import os
import json
import xml.etree.ElementTree as xml

PATH = os.path.join(os.path.dirname(__file__), 'results', 'executions')

steps = {}
total_time = 0
for f in os.listdir(PATH):
    if '.json' not in f:
        continue
    with open(os.path.join(PATH, f)) as fd:
        data = json.load(fd)
        for s in data['steps']:
            total_time += s['end'] - s['start']
            if s['success'] == False:
                name = s['name']
                if name not in steps:
                    steps[name] = 0
                steps[name] += 1
print(steps)
print("Total execution time", total_time)