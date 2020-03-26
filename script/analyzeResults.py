#!/usr/bin/env python3

import os
import json
import datetime

def macro(name, value):
    print("\\def\\%s{%s}" % (name, value))

nb_lib_version = 0
nb_lib_compiling = 0
nb_lib_debloat = 0
nb_no_clients = 0
nb_client = 0
nb_validated_debloated_client = 0
nb_test = 0
nb_failing_debloated_test = 0
execution_time = 0
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
            for i in lib['clients']:
                client = lib['clients'][i]
                execution_time += client['execution_time']
                nb_client += 1
                nb_test += client['original_test']['passing'] + client['original_test']['error'] + client['original_test']['failing']
                if client['original_test']['passing'] == client['debloat_test']['passing']:
                    nb_validated_debloated_client += 1
                nb_failing_debloated_test += max(client['original_test']['passing'] - client['debloat_test']['passing'], 0)

    macro("nbLib", len(data))
    macro("nbLibVersion", nb_lib_version)
    macro("nbLibCompiling", nb_lib_compiling)
    macro("nbLibDebloat", nb_lib_debloat)
    macro("nbNoClients", nb_no_clients)
    macro("nbTest", nb_test)
    macro("nb_failing_debloated_test", nb_failing_debloated_test)
    macro("nbClient", nb_client)
    macro("nbValidatedDebloatedClient", nb_validated_debloated_client)
    macro("executionTime", datetime.timedelta(seconds=int(execution_time)))
