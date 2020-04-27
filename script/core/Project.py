from pathlib import Path
import subprocess
import traceback
import os
from github import Github

from core.PomExtractor import PomExtractor

token = None
if 'GITHUB_OAUTH' in os.environ and len(os.environ['GITHUB_OAUTH']) > 0:
    token = os.environ['GITHUB_OAUTH']
g = Github(token)

class Project:
    def __init__(self, url):
        self.url = url
        self.name = os.path.basename(url).replace(".git", '')
        self.repo = url.replace("https://github.com/", '').replace(".git", '')
        self.path = None
        self.original_path = None
        self.pom = None
        self.releases = []
    
    def clone(self, path):
        try:
            cmd = "cd %s; ls .;git clone -q --depth=1 %s;ls .;" % (path, self.url)
            subprocess.check_call(cmd, shell=True)
            self.path = os.path.join(path, self.name)
            self.original_path = os.path.join(path, self.name)
            self.pom = PomExtractor(self.path)
            self.path = os.path.dirname(self.pom.poms[0]['path'])
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def checkout_version(self, version):
        version = version.lower().replace('v.', '').replace('v', '').replace('_', '.').replace('-', '.')
        releases = self.get_releases()
        for r in releases:
            v = r.name.lower().replace('v.', '').replace('v', '').replace('_', '.').replace('-', '.')
            try:
                index = v.index(version)
                v = v[index:]
                temp_version = version.replace('_', '.').replace('-', '.')
                if len(v) > len(temp_version):
                    temp_version += '.0'
                if v == temp_version:
                    return self.checkout_commit(r.commit.sha)
            except ValueError:
                continue
            except Exception:
                traceback.print_stack()
                continue
        return False

    def checkout_commit(self, commit):
        try:
            cmd = 'cd %s; git fetch origin %s; git checkout %s' %(self.path, commit, commit)
            subprocess.check_call(cmd, shell=True)
            self.pom = PomExtractor(self.original_path)
            self.path = os.path.dirname(self.pom.poms[0]['path'])
            return True
        except:
            return False

    def get_releases(self):
        if len(self.releases) != 0:
            return self.releases
        repo = g.get_repo(self.repo, lazy=True)
        self.releases = repo.get_tags()
        return self.releases
    
    def get_commit(self):
        cmd = 'cd %s; git rev-parse HEAD' % (self.path)
        return subprocess.check_output(cmd, shell=True).decode('UTF-8').strip()

    def clean(self):
        cmd = 'cd %s;mvn clean -B;' % (self.path)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False

    def test(self, clean=True):
        clean_cmd = 'mvn clean -B;'
        if clean is False:
            clean_cmd = ''
        cmd = 'cd %s;%s mvn test --fail-never -ntp -Dmaven.test.failure.ignore=true -B -Dmaven.javadoc.skip=true;' % (self.path, clean_cmd)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False

    def package(self):
        cmd = 'cd %s; mvn clean -B; mvn package --fail-never -ntp -Dmaven.test.error.ignore=true -Dmaven.test.failure.ignore=true -B -Dmaven.javadoc.skip=true' % (self.path)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False
    
    def copy_jar(self, dst):
        cmd = 'cd %s/target;ls .; cp *jar-with-dependencies.jar %s; ls %s' % (self.path, dst, dst)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False
    
    def copy_test_results(self, dst):
        if not os.path.exists(os.path.join(self.path, "target", "surefire-reports")):
            return False
        cmd = 'cd %s/target/; cp -r surefire-reports %s' % (self.path, dst)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False
    
    def copy_jacoco(self, dst):
        cmd = 'cd %s/target/; cp -r site/jacoco/jacoco.xml %s; cp -r site/jacoco/jacoco.csv %s' % (self.path, dst, dst)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False
    
    def copy_pom(self, dst):
        cmd = 'cd %s; cp -r %s %s' % (self.path, self.pom.poms[0]['path'], dst)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False

    def copy_report(self, dst):
        cmd = 'cd %s; cp -r debloat-* %s;' % (self.path, dst)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False

    def unzip_debloat(self, root, group_id, artifact_id, version):
        # self.pom.remove_dependency(group_id, artifact_id)
        path_jar = os.path.join(root, "%s:%s" % (group_id, artifact_id), version, "debloat", "debloat.jar")
        

        cmd = "mkdir -p %s/target/classes/; cd %s/target/classes/; jar xf %s; ls .;" % (self.path, self.path, path_jar)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except Exception as e:
            traceback.print_stack()
            return False

    def inject_debloat_library(self, root, group_id, artifact_id, version):
        path_jar = os.path.join(root, "%s:%s" % (group_id, artifact_id), version, "debloat", "debloat.jar")

        cmd = "cd %s; mvn install:install-file -Dfile=%s -DgroupId=%s -DartifactId=%s -Dversion=%s -Dpackaging=jar -B -Dmaven.javadoc.skip=true;" % (self.path, path_jar, group_id, artifact_id, version)
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except:
            return False

        # self.pom.change_depency_path(group_id, artifact_id, path_jar)
        # self.pom.write_pom()
    

    def inject_jacoco_plugin(self):
        self.pom.add_plugin("org.jacoco", "jacoco-maven-plugin", "0.8.5", [ 
            {
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
                            "text": "test"
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
        self.pom.write_pom()
        return True

    def inject_assembly_plugin(self):
        self.pom.add_plugin(None, "maven-assembly-plugin", "3.2.0", [{
            "name": "executions",
            "children": [
                {
                    "name": "execution",
                    "children": [
                        {
                            "name": "phase",
                            "text": "package"
                        },
                        {
                            "name": "goals",
                            "children": [
                                {
                                    "name": "goal",
                                    "text": "single"
                                }
                            ]
                        }
                    ]
                }]
            }, {
                "name": "configuration",
                "children": [
                    {
                        "name": "descriptorRefs",
                        "children": [
                            {
                                "name": "descriptorRef",
                                "text": "jar-with-dependencies"
                            }
                        ]
                    }
                ]
            }
        ])
        self.pom.write_pom()
        return True