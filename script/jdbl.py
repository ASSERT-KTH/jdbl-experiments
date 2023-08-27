#!/usr/bin/env python3

import argparse
from core.JDBL import JDBL
from core.Project import Project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dependency", required=True, help="The GitHub url of the debloated dependency")
    parser.add_argument("--lib-commit", help="The commit of the lib to debloat")
    parser.add_argument('-c', "--client", help="The GitHub url of the client")
    parser.add_argument("--client-commit", help="The commit of the lib to debloat")
    parser.add_argument('-v', "--version", help="The version of the libray")
    parser.add_argument('-m', "--module", help="The maven module to debloat")
    parser.add_argument('--output', help="The output folder")

    args = parser.parse_args()

    dep = Project(args.dependency)
    client = None
    if args.client is not None:
        client = Project(args.client)

    jdbl = JDBL(dep, client=client, version=args.version, commit=args.lib_commit, client_commit=args.client_commit, output=args.output, module=args.module)
    jdbl.run()
    pass
