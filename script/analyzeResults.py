#!/usr/bin/env python3

import os
import json
import datetime
import statistics

def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))
    if not isinstance(value, str):
        print("\\def\\%sStr{\\numprint{%s}\\xspace}" % (name, value))

nb_lib_version = 0
nb_lib_compiling = 0
nb_lib_debloat = 0
nb_no_clients = 0
nb_client = 0
nb_all_client = 0
nb_validated_debloated_client = 0
nb_invalidated_debloated_client = 0
nb_fail_debloat_client = 0
nb_test = 0
nb_test_client = 0
nb_failing_debloated_test = 0
execution_time = 0
nb_line_lib = 0
nb_line_client = 0

coverage_lib = []
coverage_client = []

path = os.path.join(os.path.dirname(__file__), '..', 'raw_results.json')
with open(path, 'r') as fd:
    data = json.load(fd)
    for lib_id in data:
        for version in data[lib_id]:
            nb_lib_version += 1
            lib = data[lib_id][version]
            if lib['compiled'] == True:
                nb_lib_compiling += 1
            if lib['debloat'] == True:
                nb_lib_debloat += 1
                if len(lib['clients']) == 0:
                    nb_no_clients += 1
            if 'coverage' in lib and lib['coverage'] is not None:
                nb_line_lib += lib['coverage']['nbLines']
                coverage_lib.append(lib['coverage']['coverage'])
            if lib['original_test'] is not None:
                nb_test += lib['original_test']['passing'] + lib['original_test']['error'] + lib['original_test']['failing']
            for i in lib['clients']:
                client = lib['clients'][i]
                nb_all_client += 1
                if 'execution_time' in client:
                    execution_time += client['execution_time']
                if 'original_test' in client:
                    nb_client += 1
                    nb_test_client += client['original_test']['passing'] + client['original_test']['error'] + client['original_test']['failing']
                    if 'debloat_test' in client:
                        if client['original_test']['passing'] == client['debloat_test']['passing']:
                            nb_validated_debloated_client += 1
                        else:
                            nb_invalidated_debloated_client += 1
                        nb_failing_debloated_test += max(client['original_test']['passing'] - client['debloat_test']['passing'], 0)
                    else:
                        nb_fail_debloat_client += 1
                if 'coverage_debloat' in client and client['coverage_debloat'] is not None:
                    nb_line_client += client['coverage_debloat']['nbLines']
                    coverage_client.append(client['coverage_debloat']['coverage'])

    macro("nbLib", len(data))
    macro("nbLibVersion", nb_lib_version)
    macro("nbLibCompiling", nb_lib_compiling)
    macro("nbLibDebloat", nb_lib_debloat)
    macro("nbTest", nb_test)
    macro("nbTestClient", nb_test_client)
    macro("nbFailingDebloatedTest", nb_failing_debloated_test)
    macro("nbClientAll", nb_all_client)
    macro("nbClient", nb_client)
    macro("nbFailDebloatClient", nb_fail_debloat_client)
    macro("nbValidatedDebloatedClient", nb_validated_debloated_client)
    macro("nbInvalidatedDebloatedClient", nb_invalidated_debloated_client)

    if len(coverage_lib) > 0:
        macro("meanCoverageLib", statistics.mean(coverage_lib))
        macro("medianCoverageLib", statistics.median(coverage_lib))
    if len(coverage_client) > 0:
        macro("meanCoverageClient", statistics.mean(coverage_client))
        macro("medianCoverageClient", statistics.median(coverage_client))

    macro("nbLineLib", nb_line_lib)
    macro("nbLineClient", nb_line_client)

    macro("executionTime", str(datetime.timedelta(seconds=int(execution_time))))
