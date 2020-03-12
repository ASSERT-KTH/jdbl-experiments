import os
import json

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')

runs = []
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
with open(PATH_file) as fd:
    libraries = json.load(fd)
    for id in libraries:
        lib = libraries[id]
        versions = lib['clients']
        for version in versions:
            clients = versions[version]
            if len(clients) < 4:
                continue
            for client in clients:
                cmd = 'docker run -v %s:/results -it --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git' % (OUTPUT, lib['repo_name'], client['repo_name'])
                runs.append(cmd)
                break
print(len(runs))