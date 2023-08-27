#!/usr/bin/env python3

import argparse
import tempfile
import json
import os
import sys

from core.Debloat import Debloat
from core.Project import Project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', "--lib", required=True,
                        help="The GitHub url of the debloated project")
    parser.add_argument(
        '-c', "--commit", help="The commit of the lib to debloat")
    parser.add_argument('--output', help="The output folder")
    parser.add_argument(
        "--timeout", help="Execution timeout of mvn compile/test/package", default=None)

    args = parser.parse_args()

    working_directory = tempfile.mkdtemp()

    project = Project(args.lib)
    project.clone(working_directory)

    result_path = os.path.join(args.output, project.repo.replace('/', '_'), args.commit)
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    project.checkout_commit(args.commit)
    install_result = project.compile(stdout=os.path.join(result_path, "compile.log"), timeout=args.timeout)
    if not install_result:
        print("Unable to correctly install %s" % project.repo)
        sys.exit(1)

    debloat = Debloat(project)
    depclean = debloat.depClean()

    with open(os.path.join(result_path, "depclean.json"), 'w') as fd:
        json.dump(depclean, fd, indent=1)

    # debloat.jdbl(stdout=os.path.join(result_path, "debloat.log"))
    # project.copy_report(result_path)

    try:
        dependency_tree = project.dependency_tree()
        with open(os.path.join(result_path, "dependency_tree.json"), 'w') as fd:
            json.dump(dependency_tree, fd, indent=1)
    except Exception as e:
        print(e)
        pass
