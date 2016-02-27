import os
from model.Command import Command
from model.HiveConfigFactory import HiveConfigFactory


class template(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "script", subprocess, hive_home, options)

    def create(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        service_name = args["name"]
        sub_project_folder = hive_config.hive_config_path + "/" + service_name


        if "local" in args:
            # RUN
            self._generate_from_template_file(service_name, "run", sub_project_folder, "hive.run.sh")
            # KILL
            self._generate_from_template_file(service_name, "kill", sub_project_folder, "hive.kill.sh")

        if "build" in args:
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.build.sh")
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.Dockerfile")
            self._generate_from_template_file(service_name, "build", sub_project_folder, "hive.push.sh")

        if "kubernetes" in args:
            if not os.path.exists(sub_project_folder + "/kubernetes"):
                os.makedirs(sub_project_folder + "/kubernetes")
            print "kubernetes"

    def _generate_from_template_file(self, service_name, action, sub_project_folder, template_file):
        if not os.path.exists(sub_project_folder + "/" + action):
            os.makedirs(sub_project_folder + "/" + action)

        with open("commands/templates/" + action + "/" + template_file, "r") as stream:
            template_content = stream.read()
        new_file = template_content.replace("__SERVICE_NAME__", service_name)

        with open(sub_project_folder + "/" + action + "/" + template_file, "w") as stream:
            stream.write(new_file)


