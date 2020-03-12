import xml.etree.ElementTree as xml
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

from pathlib import Path


def indent(elem, level=0):
    if len(elem):
        if elem.tail:
            elem.tail = elem.tail.strip()
        for subelem in elem:
            indent(subelem, level+1)
    return elem 

class PomExtractor:
    def __init__(self, path):
        self.namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
        self.path = path
        self.poms = []
        for p in Path(path).rglob('pom.xml'):
            f = xml.parse(p)
            self.poms.append({"path": p, "root": f.getroot()})
    
    def write_pom(self):
        for pom in self.poms:
            indent(pom["root"])
            rough_string = tostring(pom["root"], encoding="UTF-8").decode().replace("ns0:", '').replace('\n','')
            reparsed = minidom.parseString(rough_string)
            pom_content = reparsed.toprettyxml(indent="\t")
            with open(pom["path"], 'w') as fd:
                fd.write(pom_content)

    def get_artifact(self):
        return self.poms[0]["root"].find('xmlns:artifactId', namespaces=self.namespaces).text

    def get_group(self):
        return self.poms[0]["root"].find('xmlns:groupId', namespaces=self.namespaces).text

    def get_version(self):
        return self.poms[0]["root"].findall('*//xmlns:version', namespaces=self.namespaces)[0].text

    def get_version_dependency(self, group_id, artifact_id):
        for pom in self.poms:
            deps = pom["root"].findall('*//xmlns:dependency', namespaces=self.namespaces)
            for dep in deps:
                gr = dep.find('xmlns:groupId', namespaces=self.namespaces).text
                ar = dep.find('xmlns:artifactId', namespaces=self.namespaces).text
                version = dep.find('xmlns:version', namespaces=self.namespaces).text
                if gr == group_id and ar == artifact_id:
                    return version
        return None

    def change_depency_path(self, group_id, artifact_id, path):
        for pom in self.poms:
            deps = pom["root"].findall('*//xmlns:dependency', namespaces=self.namespaces)
            for dep in deps:
                gr = dep.find('xmlns:groupId', namespaces=self.namespaces).text
                ar = dep.find('xmlns:artifactId', namespaces=self.namespaces).text
                if gr == group_id and ar == artifact_id:
                    scope = dep.find('xmlns:scope', namespaces=self.namespaces)
                    if scope is None:
                        scope = SubElement(dep, "scope")
                    scope.text = "system"
                    SubElement(dep, "systemPath").text = path
                    return True
        return False

    def add_plugin(self, group_id, artifact_id, version, config):
        # check if plugin is already defined if yes, remove it
        declared_plugins = self.poms[0]["root"].findall('*//xmlns:plugin', namespaces=self.namespaces)
        for declared_plugin in declared_plugins:
            gr = declared_plugin.find('xmlns:groupId', namespaces=self.namespaces)
            if gr != group_id:
                continue
            ar = declared_plugin.find('xmlns:artifactId', namespaces=self.namespaces)
            if ar != artifact_id:
                continue
            # the plugin is the same remove it
            declared_plugin.remove()

        build_section = None
        plugins_section = None
        build = self.poms[0]["root"].findall('xmlns:build', namespaces=self.namespaces)
        print(build)
        if len(build) == 0:
            # create build section
            build_section = SubElement(self.poms[0]["root"], 'build')

            # create plugin section
            plugins_section = SubElement(build_section, 'plugins')
        else:
            build_section = build[0]
            plugins_section =  build_section.find('xmlns:plugins', namespaces=self.namespaces)

        new_plugin = SubElement(plugins_section, 'plugin')
        if group_id is not None:
            SubElement(new_plugin, 'groupId').text = group_id
        SubElement(new_plugin, 'artifactId').text = artifact_id
        SubElement(new_plugin, 'version').text = version

        def insert_config(parent, element):
            n = SubElement(parent, element['name'])
            if 'text' in element:
                n.text = element['text']
            elif 'children' in e:
                for c in element['children']:
                    insert_config(n, c)
        for e in config:
            insert_config(new_plugin, e)
            

        return self.poms[0]