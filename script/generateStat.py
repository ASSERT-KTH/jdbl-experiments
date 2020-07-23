#!/usr/bin/env python3

import os
import json
import datetime
import argparse
import zipfile

import xml.etree.ElementTree as xml

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="The output directory")

args = parser.parse_args()

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'data', 'jdbl_dataset.json')

PATH_results = os.path.join(os.path.dirname(__file__), 'results')
if args.output:
    PATH_results = os.path.abspath(args.output)

build_errors = {
    'lib': 0,
    'debloat': 0,
    'failing_test_debloat': 0,
    'client': 0,
    'client_debloat': 0,
    'none': 0
}
def parseCoverage(path, exclude=[], deps=[], debloated_class=[], classes_dep_map={}, current_lib=None, include=[]):
    coverage_results_path = os.path.join(path, "jacoco.xml")
    if not os.path.exists(coverage_results_path):
        coverage_results_path = os.path.join(path, "report.xml")
    if not os.path.exists(coverage_results_path):
        return None
    o = {
        'classes': [],
        'lib_classes': [],
        'covered_classes': {},
        'nb_lines': 0,
        'nb_covered_lines': 0,
        'all_nb_lines': 0,
        'all_nb_covered_lines': 0,
        'dep_nb_lines': 0,
        'dep_nb_covered_lines': 0,
        'coverage': 0,
        'all_coverage': 0,
        'dep_coverage': 0
    }
    coverage = None
    try:
        coverage = xml.parse(coverage_results_path).getroot()
    except:
        return None

    for package in coverage.findall("package"):
        package_name = package.attrib['name'].replace("/", ".")
        for cl in package.findall("class"):
            class_name = cl.attrib['name'].replace("/", ".")
            if len(include) > 0 and class_name not in include:
                continue
            class_covered = 0
            class_missed = 0
            if class_name not in o['classes']:
                if class_name not in deps:
                    o['classes'].append(class_name)
                else:
                    o['lib_classes'].append(class_name)
            methods = cl.findall("method")
            if current_lib is not None and class_name in debloated_class:
                if class_name in classes_dep_map:
                    current_lib['dependencies'][classes_dep_map[class_name]]['nb_method'] += len(methods)
                    current_lib['dependencies'][classes_dep_map[class_name]]['nb_debloat_method'] += len(methods)
                current_lib['nb_method'] += len(methods)
                current_lib['nb_debloat_method'] += len(methods)
            for method in methods:
                method_name = method.attrib['name'].replace("/", ".")
                for counter in method:
                    if counter.attrib['type'] != "INSTRUCTION":
                        continue
                    nb_missed = int(counter.attrib['missed'])
                    nb_covered = int(counter.attrib['covered'])
                    nb_line = nb_missed + nb_covered
                    class_covered += nb_covered
                    class_missed +=  nb_missed
                    if class_name not in exclude:
                        if class_name not in deps:
                            o['nb_lines'] += nb_line
                            o['nb_covered_lines'] += nb_covered
                        else:
                            o['dep_nb_lines'] += nb_line
                            o['dep_nb_covered_lines'] += nb_covered
                        o['all_nb_lines'] += nb_line
                        o['all_nb_covered_lines'] += nb_covered
        if class_covered > 0:
            o['covered_classes'][class_name] = class_covered / (class_covered + class_missed) 
    if o['nb_lines'] > 0:
        o['coverage'] = o['nb_covered_lines'] / o['nb_lines']
    else: 
        o['coverage'] = 0
    if o['all_nb_lines'] > 0:
        o['all_coverage'] = o['all_nb_covered_lines'] / o['all_nb_lines']
    else: 
        o['all_coverage'] = 0
    if o['dep_nb_lines'] > 0:
        o['dep_coverage'] = o['dep_nb_covered_lines'] / o['dep_nb_lines']
    else: 
        o['dep_coverage'] = 0
    return o

def get_jar_content(path):
    output = []
    zip = zipfile.ZipFile(path)
    for f in zip.filelist:
        if '.class' not in f.filename:
            continue
        cl = f.filename.replace(".class", "").replace("/", '.')
        output.append(cl)
    return output

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
invalid_libs = set()
invalid_debloat = set()
with open(PATH_file, 'r') as fd:
    data = json.load(fd)
    for lib_id in data:
        lib = data[lib_id]
        lib_id = lib['repo_name']
        lib_path = os.path.join(PATH_results, lib['repo_name'].replace('/', '_'))
        for version in lib['clients']:
            if version not in lib['releases']:
                continue
            version_path = os.path.join(lib_path, version)
            original_path = os.path.join(version_path, 'original')
            debloat_path = os.path.join(version_path, 'debloat')
            original_jar_path = os.path.join(original_path, 'original.jar')   
            
            current_lib = {
                'repo_name': lib['repo_name'],
                'compiled': os.path.exists(original_jar_path),
                'debloat': os.path.exists(os.path.join(debloat_path, 'debloat.jar')),
                'clients': {}
            }
            if current_lib['compiled'] == False:
                continue
            current_lib['original_test'] = readTestResults(original_path)
            current_lib['debloat_test'] = readTestResults(debloat_path)
            if current_lib['debloat_test'] is not None and current_lib['original_test'] is not None:
                if (current_lib['debloat_test']['error'] > current_lib['original_test']['error']) or (current_lib['debloat_test']['failing'] > current_lib['original_test']['failing']):
                    build_errors['failing_test_debloat'] += 1
            
            if not os.path.exists(original_jar_path) and os.path.exists(original_path): 
                build_errors['lib'] += 1
            
            jarClasses = []
            if os.path.exists(original_jar_path):
                jarClasses = get_jar_content(original_jar_path)
            
            if not os.path.exists(os.path.join(debloat_path, 'debloat.jar')) and os.path.exists(debloat_path):
                build_errors['debloat'] += 1
                invalid_debloat.add("%s:%s" % (lib_id, version))

            current_lib['type_nb_class'] = 0
            current_lib['type_nb_class_abstract'] = 0
            current_lib['type_nb_interface'] = 0
            current_lib['type_nb_constant'] = 0
            current_lib['type_nb_signeton'] = 0
            current_lib['type_nb_enum'] = 0
            current_lib['type_nb_exception'] = 0
            current_lib['type_nb_unknown'] = 0

            current_lib['nb_class'] = 0
            current_lib['nb_method'] = 0
            current_lib['nb_debloat_class'] = 0
            current_lib['nb_preserved_class'] = 0
            current_lib['nb_debloat_method'] = 0

            current_lib['dependencies'] = {}
            dep_classes = []
            classes_dep_map = {}
            if os.path.exists(os.path.join(debloat_path, 'debloat-dependencies-report.csv')):
                with open(os.path.join(debloat_path, 'debloat-dependencies-report.csv')) as fd:
                    lines = fd.readlines()
                    current_dep = None
                    for l in lines:
                        (dep, bloat, class_name) = l.strip().split(',')
                        if len(jarClasses) > 0 and class_name not in jarClasses:
                            continue
                        dep_classes.append(class_name)
                        classes_dep_map[class_name] = dep
                        if dep not in current_lib['dependencies']:
                            current_lib['dependencies'][dep] = {
                                'nb_class': 0,
                                'nb_debloat_class': 0,
                                'nb_preserved_class': 0,
                                'nb_method': 0,
                                'nb_debloat_method': 0,
                            }
                        current_lib['dependencies'][dep]['nb_class'] += 1
                        if "BloatedClass" in bloat:
                            current_lib['dependencies'][dep]['nb_debloat_class'] += 1
                        elif "PreservedClass" in bloat:
                            current_lib['dependencies'][dep]['nb_debloat_class'] += 1
            
            debloated_class = []
            if os.path.exists(os.path.join(debloat_path, 'debloat-report.csv')):
                with open(os.path.join(debloat_path, 'debloat-report.csv')) as fd:
                    lines = fd.readlines()
                    for l in lines:
                        if len(l.split(",")) < 2:
                            continue
                        type = l.split(",")[0]
                        class_name = l.split(",")[1].strip()
                        if ":" in class_name:
                            class_name = class_name.split(":")[0]
                        
                        if len(jarClasses) > 0 and class_name not in jarClasses:
                            continue

                        if "Method" in type:
                            if class_name in dep_classes:
                                current_lib['dependencies'][classes_dep_map[class_name]]['nb_method'] += 1
                            current_lib['nb_method'] += 1
                            if "BloatedMethod" in type:
                                current_lib['nb_debloat_method'] += 1
                                if class_name in dep_classes:
                                    current_lib['dependencies'][classes_dep_map[class_name]]['nb_debloat_method'] += 1
                        elif "Class" in type:
                            current_lib['nb_class'] += 1
                            o_type = l.split(",")[2].strip().lower()
                            
                            if "type_nb_%s" % (o_type) in current_lib:
                                current_lib["type_nb_%s" % (o_type)] += 1
                            if "BloatedClass" in type:
                                current_lib['nb_debloat_class'] += 1 
                                debloated_class.append(class_name)
                            if "PreservedClass" in type:
                                current_lib['nb_preserved_class'] += 1 

            current_lib['coverage'] = parseCoverage(debloat_path, deps=dep_classes, debloated_class=debloated_class, classes_dep_map=classes_dep_map, current_lib=current_lib, include=jarClasses)

            current_lib['debloatTime'] = ''
            if os.path.exists(os.path.join(debloat_path, 'debloat-execution-time.log')):
                with open(os.path.join(debloat_path, 'debloat-execution-time.log')) as fd:
                    # Total debloat time: 33.458 s
                    content = fd.read().strip()
                    if len(content) > 0:
                        current_lib['debloatTime'] = float(content.replace("Total debloat time: ", '').replace(" s", ''))

            if os.path.exists(original_jar_path):
                current_lib['original_jar_size'] = os.stat(original_jar_path).st_size
            else:
                current_lib['original_jar_size'] = 0
            if os.path.exists(os.path.join(debloat_path, 'debloat.jar')):
                current_lib['debloat_jar_size'] = os.stat(os.path.join(debloat_path, 'debloat.jar')).st_size
            else:
                current_lib['debloat_jar_size'] = 0
            
            if os.path.exists(os.path.join(debloat_path, 'dup.jar')):
                current_lib['workaround_jar_size'] = os.stat(os.path.join(debloat_path, 'dup.jar')).st_size
            else:
                current_lib['workaround_jar_size'] = 0

            for c in lib['clients'][version]:
                if 'artifactId' not in c or 'groupId' not in c:
                    continue
                client = "%s:%s" % (c['groupId'], c['artifactId'])
                client_path = os.path.join(version_path, "clients", c['repo_name'].replace('/', '_'))
                original_client_path = os.path.join(client_path, 'original')
                debloat_client_path = os.path.join(client_path, 'debloat')

                client_results = {
                    'repo_name': c['repo_name'],
                    'compiled': os.path.exists(os.path.join(original_client_path, "test-results")),
                    'debloat': os.path.exists(os.path.join(debloat_client_path, "test-results")),
                    'groupId': c['groupId'],
                    'artifactId': c['artifactId'],
                    'static_use': 'unknown'
                }
                path_usage = os.path.join(os.path.dirname(__file__), 'usageAnalysis', c['repo_name'].replace("/", '_') + '.csv')
                if os.path.exists(path_usage):
                    client_results['static_use'] = False
                    with open(path_usage) as usage_fd:
                        content = usage_fd.read()
                        for cl in dep_classes:
                            if cl in content:
                                client_results['static_use'] = True 
                                break
                if client_results['debloat']:
                    lib_with_clients.add(lib_id)
                    build_errors['none'] += 1
                elif os.path.exists(original_client_path):
                    if client_results['compiled']:
                        build_errors['client_debloat'] += 1
                        invalid_libs.add("%s:%s" %(lib_id, version))
                    else:
                        build_errors['client'] += 1
                current_lib['clients'][c['repo_name']] = client_results
                
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

                if lib_id not in considered_cases:
                    considered_cases[lib_id] = {
                        'repo_name': lib['repo_name'],
                        'groupId': lib['groupId'],
                        'artifactId': lib['artifactId'],
                        'releases': lib['releases'],
                        'clients': {}
                    }
                if version not in considered_cases[lib_id]['clients']:
                    considered_cases[lib_id]['clients'][version] = []
                considered_cases[lib_id]['clients'][version].append(c)
                
                client_results['original_test'] = readTestResults(original_client_path)

                exclude = []
                if current_lib['coverage'] is not None and 'classes' in current_lib['coverage']:
                    exclude = current_lib['coverage']['classes']
                client_results['coverage_original'] = parseCoverage(original_client_path, exclude)
                client_results['coverage_debloat'] = parseCoverage(debloat_client_path, exclude)
                client_results['test_cover_lib'] = False
                if client_results['coverage_original'] is not None and current_lib['coverage'] is not None:
                    for cl in client_results['coverage_original']['covered_classes']:
                        if cl in current_lib['coverage']['classes']:
                            client_results['test_cover_lib'] = True
                            break
                    pass

                client_results['debloat_test'] = readTestResults(debloat_client_path)
                
                if client_results['original_test'] is not None and client_results['debloat_test'] is not None and client_results['original_test']['passing'] == client_results['debloat_test']['passing']:
                    count_debloated_clients += 1
                out = []

                out.append("%s_%s" %(lib['repo_name'].replace("/", "_"), version))
                out.append(lib['groupId'])
                out.append(lib['artifactId'])
                out.append(version)
                out.append(str(current_lib['compiled']))
                out.append(str(current_lib['debloat']))
                out.append(str(current_lib['debloatTime']))

                if current_lib['original_test'] is not None:
                    out.append(str(current_lib['original_test']['error']))
                    out.append(str(current_lib['original_test']['failing']))
                    out.append(str(current_lib['original_test']['passing']))
                else:
                    out.append('')
                    out.append('')
                    out.append('')
                if current_lib['debloat_test'] is not None:
                    out.append(str(current_lib['debloat_test']['error']))
                    out.append(str(current_lib['debloat_test']['failing']))
                    out.append(str(current_lib['debloat_test']['passing']))
                else:
                    out.append('')
                    out.append('')
                    out.append('')

                out.append(str(current_lib['original_jar_size']))
                out.append(str(current_lib['debloat_jar_size']))
                out.append(str(current_lib['workaround_jar_size']))

                # nb classes
                out.append(str(current_lib['nb_class']))
                # nb methods
                out.append(str(current_lib['nb_method']))
                # nb debloated classes
                out.append(str(current_lib['nb_debloat_class']))
                # nb preserved classes
                out.append(str(current_lib['nb_preserved_class']))
                # nb debloated methods
                out.append(str(current_lib['nb_debloat_method']))

                count_bloated_dependencies = 0
                count_bloated_class_dependencies = 0
                count_bloated_preserved_dependencies = 0
                count_class_dependencies = 0
                count_method_dependencies = 0
                count_bloated_method_dependencies = 0
                for dep in current_lib['dependencies']:
                    count_bloated_class_dependencies += current_lib['dependencies'][dep]['nb_debloat_class']
                    count_bloated_preserved_dependencies += current_lib['dependencies'][dep]['nb_preserved_class']
                    count_class_dependencies += current_lib['dependencies'][dep]['nb_class']
                    count_method_dependencies += current_lib['dependencies'][dep]['nb_method']
                    count_bloated_method_dependencies += current_lib['dependencies'][dep]['nb_debloat_method']
                    if current_lib['dependencies'][dep]['nb_class'] == current_lib['dependencies'][dep]['nb_debloat_class']:
                        count_bloated_dependencies += 1

                # nb dependencies
                out.append(str(len(current_lib['dependencies'])))
                # nb bloated dependencies
                out.append(str(count_bloated_dependencies))
                # nb dependency class
                out.append(str(count_class_dependencies))
                # nb bloated dependency class
                out.append(str(count_bloated_class_dependencies))
                # nb preserved dependency class
                out.append(str(count_bloated_preserved_dependencies))
                # nb dependency class
                out.append(str(count_method_dependencies))
                # nb bloated dependency class
                out.append(str(count_bloated_method_dependencies))

                if current_lib['coverage'] is not None:
                    out.append(str(current_lib['coverage']['coverage']))
                    out.append(str(current_lib['coverage']['dep_coverage']))
                    out.append(str(current_lib['coverage']['all_coverage']))
                else:
                    out.append('')
                    out.append('')
                    out.append('')

                out.append(c['groupId'])
                out.append(c['artifactId'])
                out.append(str(client_results['compiled']))
                out.append(str(client_results['debloat']))
                if client_results['original_test'] is not None:
                    out.append(str(client_results['original_test']['error']))
                    out.append(str(client_results['original_test']['failing']))
                    out.append(str(client_results['original_test']['passing']))
                else:
                    out.append('')
                    out.append('')
                    out.append('')
                if client_results['debloat_test'] is not None:
                    out.append(str(client_results['debloat_test']['error']))
                    out.append(str(client_results['debloat_test']['failing']))
                    out.append(str(client_results['debloat_test']['passing']))
                else:
                    out.append('')
                    out.append('')
                    out.append('')
                if client_results['coverage_debloat'] is not None:
                    out.append(str(client_results['coverage_debloat']['coverage']))
                    del client_results['coverage_debloat']['classes']
                else:
                    out.append('')
                out.append(str(client_results['test_cover_lib']))
                out.append(str(client_results['static_use']))

                
                line = ",".join(out)
                print(line)
                csv += (line) + '\n'
            if current_lib['coverage'] is not None and 'classes' in current_lib['coverage']:
                del current_lib['coverage']['classes']
                del current_lib['coverage']['lib_classes']
            if lib_id not in results:
                results[lib_id] = {}
            results[lib_id][version] = current_lib

print("Number of error", build_errors)
print("Invalid debloated lib on client", invalid_libs)
print("Invalid debloated", invalid_debloat)
print("Lib with clients", len(lib_with_clients))
print("# successful debloated clients", count_debloated_clients)
print("Total execution time", datetime.timedelta(seconds=total_time))
with open(os.path.join(os.path.dirname(__file__), '..', 'raw_results.csv'), 'w') as fd:
    header = ['ID','"Lib.groupId"', '"Lib.artifactId"', '"Lib.version"', '"Compile"', '"Debloat"', '"Debloat.Time"', '"Lib.original.test.error"', '"Lib.original.test.failing"', '"Lib.original.test.passing"', '"Lib.debloat.test.error"', '"Lib.debloat.test.failing"', '"Lib.debloat.test.passing"', '"Size.original.jar"', '"Size.debloat.jar"', '"Size.workaround.jar"', '"Nb.class.original"', '"Nb.method.original"', '"Nb.debloated.classes"', '"Nb.preserved.classes"', '"Nb.debloated.methods"', '"Nb.Dependenies"', '"Nb.bloated.dependenies"', '"Nb.dependeny.class"', '"Nb.bloated.dependeny.class"', '"Nb.preserved.dependeny.class"', '"Nb.dependeny.method"', '"Nb.bloated.dependeny.method"', '"Lib.coverage"', '"Lib.dep.coverage"', '"Lib.all.coverage"', '"Client.groupId"', '"Client.artifactId"', '"Client.Compile"', '"Client.Debloat"', '"Client.original.test.error"', '"Client.original.test.failing"', '"Client.original.test.passing"', '"Client.debloat.test.error"', '"Client.debloat.test.failing"', '"Client.debloat.test.passing"', '"Client.coverage"', '"Cover.lib"', '"Use.lib"']
    csv = ",".join(header) + '\n' + csv
    fd.write(csv)
with open(os.path.join(os.path.dirname(__file__), '..', 'raw_results.json'), 'w') as fd:
    json.dump(results, fd, indent=1)
with open(os.path.join(os.path.dirname(__file__), 'considered_cases.json'), 'w') as fd:
    json.dump(considered_cases, fd, indent=1)