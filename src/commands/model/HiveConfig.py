import os
import sys
from ExecutionListFactory import ExecutionListFactory
from HiveMecanism import HiveMecanism
from SubProject import SubProject


class HiveConfig:
    def __init__(self, hive_file_content, hive_config_path):
        if "spec" not in hive_file_content:
            sys.exit("No spec field found in hive.yml")
        self.hive_file_content = hive_file_content
        self.hive_config_path = hive_config_path

        self.configuration = \
            hive_file_content["spec"]["configuration"] if "configuration" in hive_file_content["spec"] \
            else {}

        self.kubernetes = \
            hive_file_content["spec"]["kubernetes"] if "kubernetes" in hive_file_content["spec"] \
            else {}

        self.execution_lists = ExecutionListFactory.extract(hive_file_content)

        self.sub_projects = {}
        self.walk_folder_structure()

    def walk_folder_structure(self):
        for walk in os.walk(self.hive_config_path):
            path, folders, files = walk
            name = os.path.basename(path)
            for action in HiveMecanism.actions:
                if action in folders:
                    if name not in self.sub_projects:
                        self.sub_projects[name] = SubProject(name, path)
                    self.sub_projects[name].add_action(action)

                    if action == "kubernetes":
                        kubernetes_files = [x for x in os.walk(path + "/" + action)][0][2]
                        for file_name in kubernetes_files:
                            if "svc.yml" in file_name:
                                self.sub_projects[name].add_kubernetes_resource("service")
                            if "rc.yml" in file_name:
                                self.sub_projects[name].add_kubernetes_resource("replicationController")
                            if "sct.yml" in file_name:
                                self.sub_projects[name].add_kubernetes_resource("secret")

    def kubernetes_sub_projects(self):
        return [self.sub_projects[sub_project] for sub_project in self.sub_projects
                if len(self.sub_projects[sub_project].kubernetes) is not 0]
