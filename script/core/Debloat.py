import os
import subprocess

from xml.etree.ElementTree import tostring
from xml.dom import minidom

from core.PomExtractor import PomExtractor


def indent(elem, level=0):
    if len(elem):
        if elem.tail:
            elem.tail = elem.tail.strip()
        for subelem in elem:
            indent(subelem, level+1)
    return elem 

class Debloat:
    def __init__(self, project):
        self.project = project
        self.pom = PomExtractor(project.path)
    
    def inject_library(self):
        xml = self.pom.add_plugin("se.kth.castor", "jdbl-maven-plugin", "1.0-SNAPSHOT", [{
            "name": "executions",
            "children": [
                {
                    "name": "execution",
                    "children": [
                        {
                            "name": "goals",
                            "children": [
                                {
                                    "name": "goal",
                                    "text": "test-based-debloat"
                                }
                            ]
                        }
                    ]
                }
            ]
        }])

        xml = self.pom.add_plugin("org.jacoco", "jacoco-maven-plugin", "0.8.5", [{
            "name": "executions",
            "children": [
                {
                    "name": "execution",
                    "children": [
                        {
                            "name": "goals",
                            "children": [
                                {
                                    "name": "goal",
                                    "text": "prepare-agent"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "execution",
                    "children": [
                        {
                            "name": "id",
                            "text": "report"
                        },{
                            "name": "phase",
                            "text": "prepare-agent"
                        },{
                            "name": "goals",
                            "children": [{
                                "name": "goal",
                                "text": "report"
                            }]
                        }
                    ]
                }
            ]
        }])


        indent(xml["root"])
        rough_string = tostring(xml["root"], encoding="UTF-8").decode().replace("ns0:", '').replace('\n','')
        reparsed = minidom.parseString(rough_string)
        pom_content = reparsed.toprettyxml(indent="\t")
        with open(xml["path"], 'w') as fd:
            fd.write(pom_content)
        pass

    def run(self):
        self.inject_library()
        self.run_jdbl()
        # copy generated jar

    def run_jdbl(self):
        cmd = 'cd %s; mvn package;' % (self.project.path)
        subprocess.check_call(cmd, shell=True)