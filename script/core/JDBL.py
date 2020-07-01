import tempfile
import subprocess
import os
import shutil
import time
import json

from core.Debloat import Debloat

OUTPUT_dir = 'results' 

class JDBL:
    def __init__(self, library, client, version=None, working_directory=None, commit=None, client_commit=None, output=None):
        global OUTPUT_dir
        self.library = library
        self.lib_commit = commit
        self.client_commit = client_commit
        self.client = client
        self.version = version
        self.working_directory = working_directory
        if working_directory is None:
            self.working_directory = tempfile.mkdtemp()
        if output is not None:
            OUTPUT_dir = output
        OUTPUT_dir = os.path.abspath(OUTPUT_dir)

    def run(self):
        previous_time = time.time()
        results = {
            "start": time.time(),
            "steps": []
        }
        try:        
            print("1. Clone library...", flush=True)
            current_status = {
                "name": 'clone Library',
                "start": previous_time,
                "seccess": False
            }
            results['steps'].append(current_status)
            current_status['success'] = self.library.clone(self.working_directory)
            previous_time = time.time()
            current_status['end'] = previous_time

            if not current_status['success']:
                print("[Exit] Unable to clone the library", flush=True)
                return

            print("2. Clone client...", flush=True)
            current_status = {
                "name": 'clone client',
                "start": previous_time,
                "success": False
            }
            results['steps'].append(current_status)
            current_status['success'] = self.client.clone(self.working_directory)
            if self.client_commit is not None:
                self.client.checkout_commit(self.client_commit)
            current_status['commit'] = self.client.get_commit()

            previous_time = time.time()
            current_status['end'] = previous_time
            if not current_status['success']:
                print("[Exit] Unable to clone the library", flush=True)
                return

            dep_artifact = self.library.pom.get_artifact()
            dep_group = self.library.pom.get_group()

            if self.version is None and self.lib_library is None:
                print("3. Extract library version", flush=True)
                
                current_status = {
                    "name": 'extract library version',
                    "start": previous_time,
                    "success": False
                }
                results['steps'].append(current_status)

                self.version = self.client.pom.get_version_dependency(group_id=dep_group, artifact_id=dep_artifact)
                
                current_status['success'] = self.version is not None
                
                previous_time = time.time()
                current_status['end'] = previous_time
                if not current_status['success']:
                    print("[exit] The library version has not been found", flush=True)
                    return

            
            print("4. Checkout library version", flush=True)

            current_status = {
                "name": 'checkout library version',
                "start": previous_time,
                "success": False
            }
            results['steps'].append(current_status)
            if self.lib_commit is not None:
                print("COMMIT %s" % self.lib_commit, flush=True)
                current_status['success'] = self.library.checkout_commit(self.lib_commit)
                current_status['commit'] = self.lib_commit
            else:
                current_status['success'] = self.library.checkout_version(self.version)
                current_status['commit'] = self.library.get_commit()
            
            previous_time = time.time()
            current_status['end'] = previous_time
            if not current_status['success']:
                print("[exit] Unable to checkout commit %s" % (self.version), flush=True)
                return
            
            result_path = os.path.join(OUTPUT_dir, self.library.repo.replace('/', '_'), self.version)
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            
            lib_original_path = os.path.join(result_path, "original")
            if not os.path.exists(os.path.join(lib_original_path, "original.jar")):
                print("5. Create unmodified jar", flush=True)
                current_status = {
                    "name": 'compile original version of the library',
                    "start": previous_time,
                    "success": False
                }
                results['steps'].append(current_status)

                self.library.inject_assembly_plugin()
                if not os.path.exists(lib_original_path):
                    os.mkdir(lib_original_path)
                
                current_status['success'] = self.library.copy_pom(lib_original_path + "/pom.xml")

                current_status['success'] = self.library.package(stdout=lib_original_path + "/execution.log") and current_status['success']

                current_status['success'] = self.library.copy_jar(lib_original_path + "/original.jar") and current_status['success'] 
                current_status['success'] = self.library.copy_test_results(lib_original_path + "/test-results") and current_status['success']
                
                previous_time = time.time()
                current_status['end'] = previous_time
                if not current_status['success']:
                    print("[exit] Unable to compile the library", flush=True)
                    return
            else:
                self.library.inject_assembly_plugin()
                print("Library %s:%s with version %s already compiled" % (dep_group, dep_artifact, self.version), flush=True)

            lib_debloat_path = os.path.join(result_path, "debloat")
            if not os.path.exists(os.path.join(lib_debloat_path, "debloat.jar")):
                print("6. Create jdbl jar", flush=True)

                current_status = {
                    "name": 'create debloated jar',
                    "start": previous_time,
                    "success": False
                }
                results['steps'].append(current_status)

                shutil.copyfile(os.path.join(os.path.dirname(__file__), '..', 'coverageAgent.jar'), os.path.join(self.library.path, 'coverageAgent.jar' ))
                if not os.path.exists(lib_debloat_path):
                    os.mkdir(lib_debloat_path)
                current_status['success'] = Debloat(self.library).run(stdout=lib_debloat_path + "/execution.log")
                current_status['success'] = self.library.copy_pom(lib_debloat_path + "/pom.xml") and current_status['success']
                current_status['success'] = self.library.copy_jar(lib_debloat_path + "/debloat.jar") and current_status['success']
                current_status['success'] = self.library.copy_test_results(lib_debloat_path + "/test-results") and current_status['success']
                current_status['success'] = self.library.copy_report(lib_debloat_path) and current_status['success']

                previous_time = time.time()
                current_status['end'] = previous_time
                if not current_status['success']:
                    print("[exit] Unable to create the debloated jar", flush=True)
                    return
            else:
                print("Library %s:%s with version %s already debloated" % (dep_group, dep_artifact, self.version), flush=True)

            print("7. Execute test library debloat", flush=True)
            # TODO        

            client_results_path = os.path.join(result_path, "clients",self.client.repo.replace('/', '_'))
            if not os.path.exists(client_results_path):
                os.makedirs(client_results_path)
            elif os.path.exists(os.path.join(client_results_path, "/test-results")):
                print("[Exit] client result already present %s" % client_results_path, flush=True)
                return

            print("8. Execute client tests", flush=True)

            current_status = {
                "name": 'execute client tests',
                "start": previous_time,
                "success": False
            }
            results['steps'].append(current_status)

            original_client_results_path = os.path.join(client_results_path, "original")
            if not os.path.exists(original_client_results_path):
                os.mkdir(original_client_results_path)

            current_status['success'] = self.client.test(stdout=original_client_results_path + "/execution.log")
            
            previous_time = time.time()
            current_status['end'] = previous_time

            current_status['success'] = self.client.copy_pom(original_client_results_path + "/pom.xml") and current_status['success']
            current_status['success'] = self.client.copy_test_results(original_client_results_path + "/test-results") and current_status['success']

            if not current_status['success']:
                print("[exit] Unable to execute client tests", flush=True)
                return

            print("9. Inject debloated library in client", flush=True)

            current_status = {
                "name": 'inject debloated library in client',
                "start": previous_time,
                "success": False
            }
            results['steps'].append(current_status)
            self.client.clean()
            current_status['success'] = self.client.inject_debloat_library(OUTPUT_dir, self.library, self.version)
            current_status['success'] = self.client.unzip_debloat(OUTPUT_dir, self.library, self.version) and current_status['success']

            previous_time = time.time()
            current_status['end'] = previous_time

            if not current_status['success']:
                print("[exit] Unable to inject debloated library in client", flush=True)
                return

            print("10. Execute client tests with debloated library", flush=True)

            current_status = {
                "name": 'execute client tests with debloated library',
                "start": previous_time,
                "success": False
            }
            results['steps'].append(current_status)

            debloat_client_results_path = os.path.join(client_results_path, "debloat")
            if not os.path.exists(debloat_client_results_path):
                os.mkdir(debloat_client_results_path)

            self.client.inject_jacoco_plugin()
            current_status['success'] = self.client.copy_pom(debloat_client_results_path + "/pom.xml")
            current_status['success'] = current_status['success'] and self.client.test(clean=False,stdout=debloat_client_results_path + "/execution.log")
            current_status['success'] = current_status['success'] and self.client.copy_jacoco(debloat_client_results_path)
            current_status['success'] = current_status['success'] and self.client.copy_test_results(debloat_client_results_path + "/test-results")

            previous_time = time.time()
            current_status['end'] = previous_time

        finally:
            results['end'] = time.time()
            path_result = os.path.join(OUTPUT_dir, 'executions')
            if not os.path.exists(path_result):
                os.makedirs(path_result)
            with open(os.path.join(path_result, "%s_%s.json" % (self.library.repo.replace('/', '_'), self.client.repo.replace('/', '_'))), 'w') as fd:
                json.dump(results, fd)
            print(self.working_directory)
            #shutil.rmtree(self.working_directory)