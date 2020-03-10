import tempfile
import subprocess
import os
import shutil
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
            
            dep_artifact = self.library.pom.get_artifact()
            dep_group = self.library.pom.get_group()

            expected_dep_version = self.client.pom.get_version_dependency(group_id=dep_group, artifact_id=dep_artifact)
            
            if expected_dep_version is None:
                print("[exit] The library version has not been found")
                return

            print("4. Extract library version %s" % (expected_dep_version))
            print("5. Checkout library version")
            if not self.library.checkout_version(expected_dep_version):
                print("[exit] Unable to checkout the correct commit")
                return

            print("6. Create unmodified jar")
            result_path = os.path.join("/", "results", "%s:%s" % (dep_group, dep_artifact), expected_dep_version)
            if not os.path.exists(result_path):
                os.makedirs(result_path)
                
                self.library.inject_assembly_plugin()
                self.library.package()

                lib_original_path = os.path.join(result_path, "original")
                os.mkdir(lib_original_path)
                self.library.copy_pom(lib_original_path + "/pom.xml")
                self.library.copy_jar(lib_original_path + "/original.jar")
                self.library.copy_test_results(lib_original_path + "/test-results")

                # copy the original jar

                print("7. Create jdbl jar")
                Debloat(self.library).run()

                lib_debloat_path = os.path.join(result_path, "debloat")
                os.mkdir(lib_debloat_path)
                self.library.copy_pom(lib_debloat_path + "/pom.xml")
                self.library.copy_jar(lib_debloat_path + "/debloat.jar")
                self.library.copy_test_results(lib_debloat_path + "/test-results")
                self.library.copy_jacoco(lib_debloat_path)

                print("9. Execute test library debloat")
                # TODO
            else:
                print("Library %s:%s with version %s already debloated" % (dep_group, dep_artifact, expected_dep_version))

            client_results_path = os.path.join(result_path, "clients", "%s:%s" % (self.client.pom.get_group(), self.client.pom.get_artifact()))
            if not os.path.exists(client_results_path):
                os.makedirs(client_results_path)
            else:
                print("[Exit] client result already present %s" % client_results_path)
                return

            print("10. Execute test client")
            self.client.test()            

            original_client_results_path = os.path.join(client_results_path, "original")
            os.mkdir(original_client_results_path)
            self.client.copy_pom(original_client_results_path + "/pom.xml")
            self.client.copy_test_results(original_client_results_path + "/test-results")

            print("11. Inject debloated library in client")
            self.client.inject_debloat_library(dep_group, dep_artifact, expected_dep_version)

            print("12. Execute client tests with debloated library")
            debloat_client_results_path = os.path.join(client_results_path, "debloat")
            os.mkdir(debloat_client_results_path)
            self.client.copy_pom(debloat_client_results_path + "/pom.xml")

            self.client.test()
            self.client.copy_test_results(debloat_client_results_path + "/test-results")

        finally:
            shutil.rmtree(self.working_directory)
            pass