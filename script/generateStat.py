import os
import json
import xml.etree.ElementTree as xml

PATH = os.path.join(os.path.dirname(__file__), 'results')

build_errors = {
    'lib': 0,
    'debloat': 0,
    'client': 0,
    'client_debloat': 0,
    'none': 0
}
def readTestResults(path):
    output = {
        'error': 0,
        'failing': 0,
        'passing': 0,
        'execution_time': 0
    }
    test_results_path = os.path.join(path, "test-results")
    if not os.path.exists(test_results_path):
        return output
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

results = {}
for lib in os.listdir(PATH):
    if lib == 'executions' or lib == '.DS_Store':
        continue
    lib_path = os.path.join(PATH, lib)
    if not os.path.isdir(lib_path):
        continue
    for version in os.listdir(lib_path):
        if version == '.DS_Store':
            continue
        if lib not in results:
            results[lib] = {}
        results[lib][version] = {
            'clients': {}
        }
        version_path = os.path.join(lib_path, version)
        original_path = os.path.join(version_path, 'original')
        debloat_path = os.path.join(version_path, 'debloat')

        if not os.path.exists(os.path.join(original_path, 'original.jar')):
            build_errors['lib'] += 1
            continue

        if not os.path.exists(os.path.join(debloat_path, 'debloat.jar')):
            build_errors['debloat'] += 1
            continue

        results[lib][version]['original_test'] = readTestResults(original_path)
        results[lib][version]['debloat_test'] = readTestResults(debloat_path)
        
        clients_path = os.path.join(version_path, 'clients')
        if not os.path.exists(clients_path):
            continue

        for client in os.listdir(clients_path):
            if client == '.DS_Store':
                continue
            client_results = {}
            original_client_path = os.path.join(clients_path, client, 'original')

            if not os.path.exists(os.path.join(original_client_path, 'test-results')):
                build_errors['client'] += 1
                continue
            client_results['original_test'] = readTestResults(original_client_path)

            debloat_client_path = os.path.join(clients_path, client, 'debloat')
            if not os.path.exists(os.path.join(debloat_client_path, 'test-results')):
                build_errors['client_debloat'] += 1
                continue

            client_results['debloat_test'] = readTestResults(debloat_client_path)
            results[lib][version]['clients'][client] = client_results
            build_errors['none'] += 1
            print("Client %s on %s run the debloat version (o_test %d, d_test %d)" % (client, lib, client_results['original_test']['passing'], client_results['debloat_test']['passing']))
print("Number of error", build_errors)
with open(os.path.join(PATH, '..', '..', 'raw_results.json'), 'w') as fd:
    json.dump(results, fd, indent=1)
