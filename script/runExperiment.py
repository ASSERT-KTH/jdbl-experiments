import os
import json
import subprocess

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')

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
                cmd = 'docker run -v %s:/results -it --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git' % (OUTPUT, lib['repo_name'], client['repo_name'])
                runs.append(cmd)
                with open(os.path.join(OUTPUT, 'executions', '%s_%s.log' % (lib_name, client_name)), 'w') as fd:
                    subprocess.call(cmd, shell=True, stdout=, stderr=subprocess.STDOUT, , universal_newlines=True, stdout=fd)
                break