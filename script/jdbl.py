#!/usr/bin/env python3

import argparse
from core.JDBL import JDBL
from core.PomExtractor import PomExtractor
from core.Project import Project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dependency", required=True, help="The GitHub url of the debloated dependency")
    parser.add_argument('-c', "--client", required=True, help="The GitHub url of the client")
    parser.add_argument('-v', "--version", help="The version of the libray")

    args = parser.parse_args()

    dep = Project(args.dependency)
    client = Project(args.client)

    jdbl = JDBL(dep, client, version=args.version)
    jdbl.run()
    pass
