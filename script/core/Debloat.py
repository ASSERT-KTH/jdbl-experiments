import os
import subprocess

from core.PomExtractor import PomExtractor


class Debloat:
    def __init__(self, project):
        self.project = project
    
    def inject_library(self):
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

        self.project.pom.add_plugin("org.jacoco", "jacoco-maven-plugin", "0.8.5", [{
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


        self.project.pom.write_pom()
        pass

    def run(self):
        self.inject_library()

        cmd = 'cd %s; mvn clean -B; mvn package -e -B;' % (self.project.path)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False