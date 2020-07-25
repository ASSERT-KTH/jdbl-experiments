import os
import subprocess

from core.PomExtractor import PomExtractor
from core.Project import Project


class Debloat:
    def __init__(self, project:Project):
        self.project = project

    def inject_library(self):
        self.project.reset_surefire_plugin()
        
        self.project.pom.add_plugin("se.kth.castor", "jdbl-maven-plugin", "1.0.0", [{
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

    def run(self, stdout:str=None):
        self.inject_library()
        return self.project.package(stdout=stdout)
