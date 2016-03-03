import os
from model.Command import Command
from model.HiveConfigFactory import HiveConfigFactory


class template(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "script", subprocess, hive_home, options)

    def docker(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        service_name = args["name"]
        sub_project_folder = hive_config.hive_config_path + "/" + service_name

        if "local" in args:
            self._generate_from_template_file(service_name, "run", sub_project_folder, "hive.run.sh")
            self._generate_from_template_file(service_name, "kill", sub_project_folder, "hive.kill.sh")

        if "build" in args:
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.build.sh")
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.Dockerfile")
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.push.sh")

    def kubernetes(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        service_name = args["name"]
        sub_project_folder = hive_config.hive_config_path + "/" + service_name

        if "rc" in args:
            self._generate_from_template_file(service_name, "kubernetes", sub_project_folder, "hive.rc.yml")

        if "svc" in args:
            self._generate_from_template_file(service_name, "kubernetes", sub_project_folder, "hive.svc.yml")

        if "sct" in args:
            self._generate_from_template_file(service_name, "kubernetes", sub_project_folder, "hive.sct.yml")

    def init(self, args):

        project = args["project"]
        project_folder = self.hive_home + "/" + project if "folder" not in args \
                         else self.hive_home + "/" + args["folder"] + "/" + project

        os.makedirs(project_folder)

        with open("commands/templates/hive.yml", "r") as stream:
            content = stream.read()

        content = content.replace("__PROJECT__", project)
        if "maintainer" in args:
            content = content.replace("__MAINTAINER__", args["maintainer"])
        else:
            content = content.replace("__MAINTAINER__", "not define")

        with open(project_folder + "/hive.yml", "w") as stream:
            stream.write(content)

    def _generate_from_template_file(self, service_name, action, sub_project_folder, template_file):
        if not os.path.exists(sub_project_folder + "/" + action):
            os.makedirs(sub_project_folder + "/" + action)

        with open("commands/templates/" + action + "/" + template_file, "r") as stream:
            template_content = stream.read()
        new_file = template_content.replace("__SERVICE_NAME__", service_name)

        with open(sub_project_folder + "/" + action + "/" + template_file, "w") as stream:
            stream.write(new_file)


