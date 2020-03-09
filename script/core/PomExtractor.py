import xml.etree.ElementTree as xml
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

from pathlib import Path



class PomExtractor:
    def __init__(self, path):
        self.namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
        self.path = path
        self.poms = []
        print(Path(path), Path(path).rglob('pom.xml'))
        for p in Path(path).rglob('pom.xml'):
            f = xml.parse(p)
            self.poms.append({"path": p, "root": f.getroot()})
    
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

    def add_plugin(self, group_id, artifact_id, version, config):
        plugins_section = None
        plugins = self.poms[0]["root"].findall('*//xmlns:plugins', namespaces=self.namespaces)
        if len(plugins) == 0:
            build_section = None
            build = self.poms[0]["root"].findall('*//xmlns:build', namespaces=self.namespaces)
            if len(build) == 0:
                # create build section
                build_section = SubElement(self.poms[0]["root"], 'build')
            else:
                build_section = build[0]
            # create plugin section
            build_section = SubElement(build_section, 'plugins')
        else:
            plugins_section = plugins[0]
        new_plugin = SubElement(plugins_section, 'plugin')
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