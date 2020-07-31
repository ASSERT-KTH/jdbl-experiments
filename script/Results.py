from typing import List

import os
import json


class Results:
    def __init__(self):
        self.libs: List[Library] = list()
        pass

    def __str__(self):
        output = f"{len(self.libs)} libraries:"
        for e in self.libs:
            output += "\n\t" + "\n\t".join(str(e).split("\n"))
        return output


class Library:
    def __init__(self):
        self.repo: str
        self.versions: List[Version] = list()

    def id(self):
        return self.repo.replace("/", "_")

    def __str__(self):
        output = f"{self.repo} has {len(self.versions)} versions:"
        for e in self.versions:
            output += "\n\t" + "\n\t".join(str(e).split("\n"))
        return output


class Version:
    def __init__(self, library: Library):
        self.library = library
        self.version: str
        self.compiled = False
        self.debloat = False
        self.original_test: TestResults
        self.debloat_test: TestResults
        self.coverage: Coverage

        self.nb_class: int
        self.nb_method: int
        self.nb_debloat_class: int
        self.nb_preserved_class: int
        self.nb_debloat_method: int

        self.type_nb_class: int
        self.type_nb_class_abstract: int
        self.type_nb_interface: int
        self.type_nb_constant: int
        self.type_nb_signeton: int
        self.type_nb_enum: int
        self.type_nb_exception: int
        self.type_nb_unknown: int

        self.debloat_time: float
        self.original_execution_time: float
        self.debloat_execution_time: float
        
        self.original_jar_size: int
        self.debloat_jar_size: int
        self.workaround_jar_size: int

        self.clients: List[Client] = list()

    def __getitem__(self, index):
        print(index)
        return self.clients[index]

    def __str__(self):
        output = f"{self.version} Compile: {self.compiled} Debloat: {self.debloat} has {len(self.clients)} clients:"
        for e in self.clients:
            output += "\n\t" + "\n\t".join(str(e).split("\n"))
        return output


class Client:
    def __init__(self, version: Version):
        self.version = version
        self.repo: str
        self.compiled = False
        self.debloat = False
        self.static_use = False
        self.test_cover_lib = False
        self.original_test: TestResults
        self.debloat_test: TestResults
        self.coverage_original: Coverage
        self.coverage_debloat: Coverage
        self.original_execution_time: float
        self.debloat_execution_time: float

    def id(self):
        return self.repo.replace("/", "_")

    def __str__(self):
        output = f"{self.repo} Compile: {self.compiled} Debloat: {self.debloat}"
        return output


class Dependency:
    def __init__(self):
        self.name: str
        self.nb_class: int
        self.nb_debloat_class: int
        self.nb_preserved_class: int
        self.nb_method: int
        self.nb_debloat_method: int

    def __str__(self):
        output = f"{self.name} bloated classes: {self.nb_debloat_class} (preserved: {self.nb_preserved_class})/{self.nb_class} bloated methods: {self.nb_debloat_method}/{self.nb_method}"
        return output


class TestResults:
    def __init__(self):
        self.error: int
        self.failing: int
        self.passing: int
        self.execution_time: float

    def nb_test(self):
        return self.passing + self.failing + self.error

    def is_passing(self):
        return self.failing + self.error == 0


class Coverage:
    def __init__(self):
        self.covered_classes: {}
        self.nb_lines: int
        self.nb_covered_lines: int
        self.all_nb_lines: int
        self.all_nb_covered_lines: int
        self.dep_nb_lines: int
        self.dep_nb_covered_lines: int
        self.coverage: float
        self.all_coverage: float
        self.dep_coverage: int


def _extract_dependencies(deps) -> List[Dependency]:
    output = []
    for dep in deps:
        dependency = Dependency()
        dependency.name = dep

        dependency.nb_class = deps[dep]['nb_class']
        dependency.nb_debloat_class = deps[dep]['nb_debloat_class']
        dependency.nb_preserved_class = deps[dep]['nb_preserved_class']
        dependency.nb_method = deps[dep]['nb_method']
        dependency.nb_debloat_method = deps[dep]['nb_debloat_method']

        output.append(dependency)
    return output


def _extract_coverage(cov) -> Coverage:
    if cov is None:
        return None

    coverage = Coverage()
    Coverage()
    coverage.nb_lines = cov['nb_lines']
    coverage.nb_covered_lines = cov['nb_covered_lines']
    coverage.all_nb_lines = cov['all_nb_lines']
    coverage.all_nb_covered_lines = cov['all_nb_covered_lines']
    coverage.dep_nb_lines = cov['dep_nb_lines']
    coverage.dep_nb_covered_lines = cov['dep_nb_covered_lines']
    coverage.coverage = cov['coverage']
    coverage.all_coverage = cov['all_coverage']
    coverage.dep_coverage = cov['dep_coverage']
    return coverage


def _extract_test_results(test) -> TestResults:
    if test is None:
        return None

    test_results = TestResults()

    test_results.error = test['error']
    test_results.failing = test['failing']
    test_results.passing = test['passing']
    test_results.execution_time = test['execution_time']

    return test_results


results = Results()
with open(os.path.join(os.path.dirname(__file__), '..', 'raw_results.json'), 'r') as fd:
    data = json.load(fd)
    for lib_id in data:
        library = Library()
        results.libs.append(library)
        library.repo = lib_id
        for v in data[lib_id]:
            if "woodstox" in lib_id and (v == "6.1.1" or v == "6.0.2"):
                continue
            version = Version(library)
            library.versions.append(version)
            version.version = v
            l = data[lib_id][v]

            version.compiled = l['compiled']
            version.debloat = l['debloat']

            version.type_nb_class = l['type_nb_class']
            version.type_nb_class_abstract = l['type_nb_class_abstract']
            version.type_nb_interface = l['type_nb_interface']
            version.type_nb_constant = l['type_nb_constant']
            version.type_nb_signeton = l['type_nb_signeton']
            version.type_nb_enum = l['type_nb_enum']
            version.type_nb_exception = l['type_nb_exception']
            version.type_nb_unknown = l['type_nb_unknown']
            version.nb_class = l['nb_class']
            version.nb_method = l['nb_method']
            version.nb_debloat_class = l['nb_debloat_class']
            version.nb_preserved_class = l['nb_preserved_class']
            version.nb_debloat_method = l['nb_debloat_method']
            version.debloat_time = l['debloat_time']
            version.original_execution_time = l['original_execution_time']
            version.debloat_execution_time = l['debloat_execution_time']
            version.original_jar_size = l['original_jar_size']
            version.debloat_jar_size = l['debloat_jar_size']
            version.workaround_jar_size = l['workaround_jar_size']

            version.dependencies = _extract_dependencies(l['dependencies'])

            version.coverage = _extract_coverage(l['coverage'])
            version.original_test = _extract_test_results(l['original_test'])
            version.debloat_test = _extract_test_results(l['debloat_test'])

            for i in l['clients']:
                c = l['clients'][i]
                client = Client(version)
                version.clients.append(client)
                client.repo = c['repo_name']

                client.compiled = c['compiled']
                client.debloat = c['debloat']
                client.groupId = c['groupId']
                client.artifactId = c['artifactId']
                client.static_use = c['static_use']
                client.test_cover_lib = c['test_cover_lib']
                client.original_test = _extract_test_results(
                    c['original_test'])
                client.debloat_test = _extract_test_results(c['debloat_test'])

                client.coverage_original = _extract_coverage(
                    c['coverage_original'])
                client.coverage_debloat = _extract_coverage(
                    c['coverage_debloat'])
                client.original_execution_time = c['original_execution_time']
                client.debloat_execution_time = c['debloat_execution_time']
