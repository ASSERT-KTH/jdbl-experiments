#!/usr/bin/env python3

import argparse, tempfile, os, json
import xml.etree.ElementTree as xml

from core.Project import Project

def readTestResults(path):
    output = {
        'error': 0,
        'failing': 0,
        'passing': 0,
        'execution_time': 0
    }
    test_results_path = os.path.join(path, "surefire-reports")
    if not os.path.exists(test_results_path):
        test_results_path = os.path.join(path, "target", "surefire-reports")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", required=True, help="The url to the git repository")
    parser.add_argument("--commit", required=True, help="The commit of the lib to debloat")
    parser.add_argument("--iteration", type=int, default=3, help="The number of test execution")

    args = parser.parse_args()

    working_directory = tempfile.mkdtemp()

    project = Project(args.url)
    project.clone(working_directory)
    project.checkout_commit(args.commit)
    output = {
        "commit": project.get_commit(),
        "test_results": []
    }
    for i in range(0, args.iteration):
        project.test(stdout="output.log")
        output['test_results'].append(readTestResults(project.path))
    print(json.dumps(output))
