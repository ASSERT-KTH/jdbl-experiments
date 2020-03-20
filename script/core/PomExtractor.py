import xml.etree.ElementTree as xml
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

from pathlib import Path


def stripNs(el):
  '''Recursively search this element tree, removing namespaces.'''
  if el.tag.startswith("{"):
    el.tag = el.tag.split('}', 1)[1]  # strip namespace
  for k in el.attrib.keys():
    if k.startswith("{"):
      k2 = k.split('}', 1)[1]
      el.attrib[k2] = el.attrib[k]
      del el.attrib[k]
  for child in el:
    stripNs(child)

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
            root = f.getroot()
            stripNs(root)
            if root.attrib.get('schemaLocation') is not None:
                root.attrib.pop('schemaLocation')
            self.poms.append({"path": p, "root": root})
    
    def write_pom(self):
        for pom in self.poms:
            indent(pom["root"])
            rough_string = tostring(pom["root"], encoding="UTF-8").decode().replace("ns0:", '').replace('\n','')
            reparsed = minidom.parseString(rough_string)
            pom_content = reparsed.toprettyxml(indent="\t")
            with open(pom["path"], 'w') as fd:
                fd.write(pom_content)

    def get_artifact(self):
        r = self.poms[0]["root"].find('artifactId')
        if r is not None:
            return r.text
        return ''

    def get_group(self):
        r = self.poms[0]["root"].find('groupId')
        if r is not None:
            return r.text
        return ''

    def get_version(self):
        r = self.poms[0]["root"].findall('*//version')[0]
        if r is not None:
            return r.text
        return ''

    def remove_dependency(self, group_id, artifact_id):
        for pom in self.poms:
            prop_parents = self.poms[0]["root"].findall('*//dependency/..')
            for parent in prop_parents:
                for dep in parent:
                    gr = dep.find('groupId')
                    if gr is not None:
                        gr = gr.text
                    if group_id != gr:
                        continue
                    ar = dep.find('artifactId')
                    if ar is not None:
                        ar = ar.text
                    if ar != artifact_id:
                        continue
                    parent.remove(dep)
                    return dep
        return None

    def get_version_dependency(self, group_id, artifact_id):
        for pom in self.poms:
            deps = pom["root"].findall('*//dependency')
            for dep in deps:
                gr = dep.find('groupId').text
                ar = dep.find('artifactId').text
                if gr == group_id and ar == artifact_id:
                    version = dep.find('version')
                    if version is not None:
                        version = version.text
                    return version
        return None

    def change_depency_path(self, group_id, artifact_id, path):
        for pom in self.poms:
            deps = pom["root"].findall('*//dependency')
            for dep in deps:
                gr = dep.find('groupId').text
                ar = dep.find('artifactId').text
                if gr == group_id and ar == artifact_id:
                    scope = dep.find('scope')
                    if scope is None:
                        scope = SubElement(dep, "scope")
                    scope.text = "system"
                    SubElement(dep, "systemPath").text = path
                    return True
        return False

    def add_plugin(self, group_id, artifact_id, version, config):
        # check if plugin is already defined if yes, remove it
        prop_parents = self.poms[0]["root"].findall('*//plugin/..')
        for parent in prop_parents:
            for declared_plugin in parent:
                gr = declared_plugin.find('groupId')
                if gr is not None:
                    gr = gr.text
                if group_id != gr:
                    continue
                ar = declared_plugin.find('artifactId')
                if ar is not None:
                    ar = ar.text
                if ar != artifact_id:
                    continue
                # the plugin is the same remove it
                parent.remove(declared_plugin)

        build_section = None
        plugins_section = None
        build = self.poms[0]["root"].findall('build')
        if len(build) == 0:
            # create build section
            build_section = SubElement(self.poms[0]["root"], 'build')

            # create plugin section
            plugins_section = SubElement(build_section, 'plugins')
        else:
            build_section = build[0]
            plugins_section =  build_section.find('plugins')

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