#!/usr/bin/env python3

import os
import json
import datetime
import xml.etree.ElementTree as xml

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')

PATH_results = os.path.join(os.path.dirname(__file__), 'results')

build_errors = {
    'lib': 0,
    'debloat': 0,
    'client': 0,
    'client_debloat': 0,
    'none': 0
}
def parseCoverage(path, exclude=[]):
    coverage_results_path = os.path.join(path, "jacoco.csv")
    if not os.path.exists(coverage_results_path):
        return None
    o = {
        'classes': [],
        'coveredClasses': {},
        'nbLines': 0,
        'nbCoveredLines': 0,
        'coverage': 0
    }
    with open(coverage_results_path, 'r') as fd:
        lines = fd.readlines()
        if len(lines) == 0:
            return None
        header = lines[0].split(',')
        for l in lines[1:]:
            r = {}
            values = l.split(',')
            for i in range(0, len(header)):
                v = values[i]
                if v.isdigit():
                    v = int(v)
                r[header[i]] = v
            cl = '%s.%s' % (r['PACKAGE'], r['CLASS'])
            if cl not in o['classes']:
                o['classes'].append(cl)
            if cl not in exclude:
                o['nbLines'] += r['LINE_MISSED'] + r['LINE_COVERED']
                o['nbCoveredLines'] += r['LINE_COVERED']
            if r['LINE_COVERED'] > 0:
                o['coveredClasses'][cl] = r['LINE_COVERED'] / (r['LINE_COVERED'] + r['LINE_MISSED']) 
    o['coverage'] = o['nbCoveredLines'] / o['nbLines']
    return o

def readTestResults(path):
    output = {
        'error': 0,
        'failing': 0,
        'passing': 0,
        'execution_time': 0
    }
    test_results_path = os.path.join(path, "test-results")
    if not os.path.exists(test_results_path):
        return None
    for test in os.listdir(test_results_path):
        if ".xml" not in test:
            continue
        test_path = os.path.join(test_results_path, test)
        try:
            test_results = xml.parse(test_path).getroot()
            if test_results.get('time') is not None:
                output['execution_time'] += float(test_results.get('time'))  
            if test_results.get('errors') is not None:
                output['error'] += int(test_results.get('errors'))
            if test_results.get('failures') is not None:
                output['failing'] += int(test_results.get('failures'))
            if test_results.get('failed') is not None:
                output['failing'] += int(test_results.get('failed'))
            if test_results.get('tests') is not None:
                output['passing'] += int(test_results.get('tests')) - int(test_results.get('errors')) - int(test_results.get('failures'))
            if test_results.get('passed') is not None:
                output['passing'] += int(test_results.get('passed'))
        except:
            pass
    return output       

csv = ""
lib_with_clients = set()
count_debloated_clients = 0
total_time = 0
results = {}
considered_cases = {}

with open(PATH_file, 'r') as fd:
    data = json.load(fd)
    for lib_id in data:
        lib = data[lib_id]
        lib_path = os.path.join(PATH_results, lib_id)
        for version in lib['clients']:
            if len(lib['clients'][version]) < 4:
                continue
            version_path = os.path.join(lib_path, version)
            original_path = os.path.join(version_path, 'original')
            debloat_path = os.path.join(version_path, 'debloat')     
            
            if lib_id not in results:
                results[lib_id] = {}
            results[lib_id][version] = {
                'compiled': os.path.exists(original_path),
                'debloat': os.path.exists(debloat_path),
                'clients': {},
                'coverage': parseCoverage(debloat_path)
            }
            results[lib_id][version]['original_test'] = readTestResults(original_path)
            results[lib_id][version]['debloat_test'] = readTestResults(debloat_path)

            results[lib_id][version]['nbClass'] = 0
            results[lib_id][version]['nbMethod'] = 0
            results[lib_id][version]['nbDebloatClass'] = 0
            results[lib_id][version]['nbDebloatMethod'] = 0

            if os.path.exists(os.path.join(debloat_path, 'debloat-report.csv')):
                with open(os.path.join(debloat_path, 'debloat-report.csv')) as fd:
                    lines = fd.readlines()
                    for l in lines:
                        (type, name) = l.split(", ")
                        if "Method" in type:
                            results[lib_id][version]['nbMethod'] += 1
                            if "BloatedMethod" in type:
                                results[lib_id][version]['nbDebloatMethod'] += 1
                        elif "Class" in type:
                            results[lib_id][version]['nbClass'] += 1
                            if "BloatedClass" in type:
                                results[lib_id][version]['nbDebloatClass'] += 1 
            results[lib_id][version]['dependencies'] = {}
            if os.path.exists(os.path.join(debloat_path, 'debloat-dependencies-report.csv')):
                with open(os.path.join(debloat_path, 'debloat-dependencies-report.csv')) as fd:
                    lines = fd.readlines()
                    current_dep = None
                    for l in lines:
                        if ", " not in l:
                            current_dep = l.strip()
                            results[lib_id][version]['dependencies'][current_dep] = {
                                'nbClass': 0,
                                'nbDebloatClass': 0,
                            }
                        else:   
                            (type, name) = l.strip().split(", ")
                            results[lib_id][version]['dependencies'][current_dep]['nbClass'] += 1
                            if "BloatedClass" in type:
                                results[lib_id][version]['dependencies'][current_dep]['nbDebloatClass'] += 1 
            results[lib_id][version]['debloatTime'] = -1
            if os.path.exists(os.path.join(debloat_path, 'debloat-execution-time.log')):
                with open(os.path.join(debloat_path, 'debloat-execution-time.log')) as fd:
                    # Total debloat time: 33.458 s
                    results[lib_id][version]['debloatTime'] = float(fd.read().strip().replace("Total debloat time: ", '').replace(" s", ''))

            for c in lib['clients'][version]:
                if 'artifactId' not in c or 'groupId' not in c:
                    continue
                client = "%s:%s" % (c['groupId'], c['artifactId'])
                client_path = os.path.join(version_path, "clients", client)
                client_results = {}
                results[lib_id][version]['clients'][client] = client_results
                original_client_path = os.path.join(client_path, 'original')
                filename = "%s_%s.json" % (lib['repo_name'].replace('/', '_'), c['repo_name'].replace('/', '_'))
                path_execution_log = os.path.join(PATH_results, 'executions', filename)
                if os.path.exists(path_execution_log):
                    with open(path_execution_log) as fd:
                        try:
                            execution_data = json.load(fd)
                            client_results['execution_time'] = execution_data['end'] - execution_data['start']
                            total_time += execution_data['end'] - execution_data['start']
                        except:
                            print("%s is not a valid json" % path_execution_log)
                            continue

                if not os.path.exists(os.path.join(original_client_path, 'test-results')):
                    build_errors['client'] += 1
                    continue
                if lib_id not in considered_cases:
                    considered_cases[lib_id] = {
                        'repo_name': lib['repo_name'],
                        'groupId': lib['groupId'],
                        'artifactId': lib['artifactId'],
                        'clients': {}
                    }
                if version not in considered_cases[lib_id]['clients']:
                    considered_cases[lib_id]['clients'][version] = []
                considered_cases[lib_id]['clients'][version].append(c)
                
                client_results['original_test'] = readTestResults(original_client_path)

                debloat_client_path = os.path.join(client_path, 'debloat')
                if not os.path.exists(os.path.join(debloat_client_path, 'test-results')):
                    build_errors['client_debloat'] += 1
                    continue
                
                exclude = []
                if results[lib_id][version]['coverage'] is not None and 'classes' in results[lib_id][version]['coverage']:
                    exclude = results[lib_id][version]['coverage']['classes']
                client_results['coverage_debloat'] = parseCoverage(debloat_client_path, exclude)
                client_results['test_cover_lib'] = False
                if client_results['coverage_debloat'] is not None and results[lib_id][version]['coverage'] is not None:
                    for cl in client_results['coverage_debloat']['coveredClasses']:
                        if cl in results[lib_id][version]['coverage']['classes']:
                            client_results['test_cover_lib'] = True
                            break
                    pass

                client_results['debloat_test'] = readTestResults(debloat_client_path)
                results[lib_id][version]['clients'][client] = client_results
                build_errors['none'] += 1
                lib_with_clients.add(lib_id)
                if client_results['original_test']['passing'] == client_results['debloat_test']['passing']:
                    count_debloated_clients += 1
                out = []
                out.append(lib['groupId'])
                out.append(lib['artifactId'])
                out.append(version)
                out.append(str(os.stat(os.path.join(original_path, 'original.jar')).st_size))
                out.append(str(os.stat(os.path.join(debloat_path, 'debloat.jar')).st_size))

                # nb classes
                out.append(str(results[lib_id][version]['nbClass']))
                # nb methods
                out.append(str(results[lib_id][version]['nbMethod']))
                # nb debloated classes
                out.append(str(results[lib_id][version]['nbDebloatClass']))
                # nb debloated methods
                out.append(str(results[lib_id][version]['nbDebloatMethod']))

                out.append(c['groupId'])
                out.append(c['artifactId'])
                out.append(str(client_results['original_test']['error']))
                out.append(str(client_results['original_test']['failing']))
                out.append(str(client_results['original_test']['passing']))

                out.append(str(client_results['debloat_test']['error']))
                out.append(str(client_results['debloat_test']['failing']))
                out.append(str(client_results['debloat_test']['passing']))
                
                line = "\t".join(out)
                print(line)
                csv += (line) + '\n'

print("Number of error", build_errors)
print("Lib with clients", len(lib_with_clients))
print("# successful debloated clients", count_debloated_clients)
print("Total execution time", datetime.timedelta(seconds=total_time))
with open(os.path.join(PATH_results, '..', '..', 'raw_results.csv'), 'w') as fd:
    fd.write(csv)
with open(os.path.join(PATH_results, '..', '..', 'raw_results.json'), 'w') as fd:
    json.dump(results, fd, indent=1)
with open(os.path.join(PATH_results, '..', 'considered_cases.json'), 'w') as fd:
    json.dump(considered_cases, fd, indent=1)