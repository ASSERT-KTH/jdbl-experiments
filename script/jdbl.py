#!/usr/bin/env python3

import argparse
from core.JDBL import JDBL
from core.PomExtractor import PomExtractor
from core.Project import Project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dependency", required=True, help="The GitHub url of the debloated dependency")
    parser.add_argument('-c', "--client", required=True, help="The GitHub url of the client")

    parser.add_argument('-g', "--groupId", help="The groupId of the dependency")
    parser.add_argument('-a', "--artifactId", help="The artifactId of the dependency")
    args = parser.parse_args()

    dep = Project(args.dependency)
    client = Project(args.client)

    jdbl = JDBL(dep, client, groupId=args.groupId, artifactId=args.artifactId)
    jdbl.run()
    # dep_pom = PomExtractor("/var/folders/z4/sdq_r5xs4h91kjx05vqn7ntr0000gn/T/tmpyfa2c12_/pdfbox/")
    # client_pom = PomExtractor("/var/folders/z4/sdq_r5xs4h91kjx05vqn7ntr0000gn/T/tmpyfa2c12_/serverless/")
    # # dep_pom.get_artifact()
    # print(client_pom.get_version_dependency(group_id=dep_pom.get_group(), artifact_id="pdfbox"))
    pass
