#!/usr/bin/env python3

import argparse, tempfile, subprocess,os
from core.JDBL import JDBL
from core.Project import Project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", required=True, help="The GitHub url")
    parser.add_argument("--commit", help="The commit of the repo to analyze")
    parser.add_argument('--output', help="The output folder")

    args = parser.parse_args()

    project = Project(args.url)

    working_directory = tempfile.mkdtemp()
    project.clone(working_directory)
    
    if "commit" in args and args.commit is not None:
        project.checkout_commit(args.commit)
    
    cmd = "java -jar extractclassusage.jar %s 2>/dev/null" %(project.path)
    output = subprocess.check_output(cmd, shell=True)
    if args.output is not None:
        with open(os.path.join(args.output, project.repo.replace("/", "_") + ".csv"), 'wb') as fd:
            fd.write(output)
    else:
        print(output)