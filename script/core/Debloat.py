import os
import subprocess

from core.PomExtractor import PomExtractor


class Debloat:
    def __init__(self, project):
        self.project = project
    
    def inject_library(self):
        self.project.pom.remove_plugin('org.apache.maven.plugins', 'maven-surefire-plugin')
        self.project.inject_jacoco_plugin()
        self.project.pom.add_plugin("se.kth.castor", "jdbl-maven-plugin", "1.0-SNAPSHOT", [{
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

        self.project.pom.write_pom()
        pass

    def run(self):
        self.inject_library()
        return self.project.package()