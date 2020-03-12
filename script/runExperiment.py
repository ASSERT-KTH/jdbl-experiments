#!/usr/bin/env python3

import os
import json
import subprocess

token = None
if 'GITHUB_OAUTH' in os.environ and len(os.environ['GITHUB_OAUTH']) > 0:
    token = os.environ['GITHUB_OAUTH']

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')

timeout = 15 * 60 # 15min

runs = []
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
with open(PATH_file) as fd:
    libraries = json.load(fd)
    for id in libraries:
        lib = libraries[id]
        lib_name = os.path.basename(lib['repo_name'])
        versions = lib['clients']
        for version in versions:
            clients = versions[version]
            if len(clients) < 4:
                continue
            for client in clients:
                client_name = os.path.basename(client['repo_name'])
                print("Run %s %s" % (lib['repo_name'], client['repo_name']))
                cmd = 'docker run -e GITHUB_OAUTH="%s" -v %s:/results -it --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git' % (token, OUTPUT, lib['repo_name'], client['repo_name'])
                runs.append(cmd)
                with open(os.path.join(OUTPUT, 'executions', '%s_%s.log' % (lib_name, client_name)), 'w') as fd:
                    try:
                        subprocess.call(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, stdout=fd, timeout=timeout)
                    except Exception as e:
                        print(e)
                        pass
                break