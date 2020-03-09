import tempfile
import subprocess
import os
import shutil
from core.PomExtractor import PomExtractor
from core.Debloat import Debloat


class JDBL:
    def __init__(self, library, client, groupId=None, artifactId=None, working_directory=None):
        self.library = library
        self.client = client
        self.groupId = groupId
        self.artifactId = artifactId
        self.working_directory = working_directory
        if working_directory is None:
            self.working_directory = tempfile.mkdtemp()
        print(self.working_directory)

    def run(self):
        try:        
            print("1. Clone library...")
            self.library.clone(self.working_directory)
            print("2. Clone client...")
            self.client.clone(self.working_directory)

            print("3. Extract library name")
            dep_extractor = PomExtractor(os.path.join(self.working_directory, self.library.name))
            dep_artifact = dep_extractor.get_artifact()
            dep_group = dep_extractor.get_group()
            client_extractor = PomExtractor(os.path.join(self.working_directory, self.client.name))
            expected_dep_version = client_extractor.get_version_dependency(group_id=dep_group, artifact_id=dep_artifact)
            
            if expected_dep_version is None:
                print("[exit] The library version has not been found")
                return

            print("4. Extract library version %s" % (expected_dep_version))
            print("5. Checkout library version")
            if not self.library.checkout_version(expected_dep_version):
                print("[exit] Unable to checkout the correct commit")
                return

            print("6. Create unmodified jar")
            self.library.package()
            self.library.copyJar("/results/original.jar")
            self.library.copyTestResults("/results/original_tests")

            # copy the original jar

            print("7. Create jdbl jar")
            Debloat(self.library).run()
            self.library.copyJar("/results/jdbl.jar")
            self.library.copyTestResults("/results/jdbl_tests")
            self.library.copyJacoco("/results/jacoco.xml")

            # copy the original jar
            print("8. Execute test: unmodified")

            print("9. Execute test: jdbl")

            print("10. Execute test: proguard")
        finally:
            shutil.rmtree(self.working_directory)
            pass


