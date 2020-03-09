from pathlib import Path
import subprocess
import os
from github import Github

g = Github("eac54c8e366cb4781d7d42f8167f16358247d74d")

class Project:
    def __init__(self, url):
        self.url = url
        self.name = os.path.basename(url).replace(".git", '')
        self.repo = url.replace("https://github.com/", '').replace(".git", '')
        self.path = None
        self.releases = []
    
    def clone(self, path):
        cmd = "cd %s; ls .;git clone --depth=1 %s;ls .;" % (path, self.url)
        subprocess.check_call(cmd, shell=True)
        self.path = os.path.join(path, self.name)

    def checkout_version(self, version):
        releases = self.get_releases()
        for r in releases:
            v = r.name.replace('v.', '').replace('v', '')
            try:
                index = v.index(version)
                v = v[index:]
                temp_version = version
                if len(v) > len(temp_version):
                    temp_version += '.0'
                if v == temp_version:
                    self.checkout_commit(r.commit.sha)
                    return True
            except:
                continue
        return False

    def checkout_commit(self, commit):
        cmd = 'cd %s; git fetch origin %s; git checkout %s' %(self.path, commit, commit)
        subprocess.check_call(cmd, shell=True)
        return True

    def modules(self):
        pass

    def get_releases(self):
        if len(self.releases) != 0:
            return self.releases
        repo = g.get_repo(self.repo, lazy=True)
        self.releases = repo.get_tags()
        return self.releases
    
    def package(self):
        cmd = 'cd %s; mvn package' % (self.path)
        subprocess.check_call(cmd, shell=True)
    
    def copyJar(self, dst):
        cmd = 'cd %s/target;ls .; cp *.jar %s; ls %s' % (self.path, dst, dst)
        subprocess.check_call(cmd, shell=True)
    
    def copyTestResults(self, dst):
        cmd = 'cd %s/target/; cp -r surefire-reports %s; ls %s' % (self.path, dst, dst)
        subprocess.check_call(cmd, shell=True)
    
    def copyJacoco(self, dst):
        cmd = 'cd %s/target/; cp -r report.xml %s; ls %s' % (self.path, dst, dst)
        subprocess.check_call(cmd, shell=True)