import sys
from model.Command import Command
from model.HiveConfigFactory import HiveConfigFactory
from business.FileGenerator import FileGenerator


class do(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "kubernetes", subprocess, hive_home, options)

    # commands
    def build(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        sub_projects = self._find_sub_projects(args["subprojects"], hive_config, "build")
        self._execute_templated_command(
                "./build.sh",
                args["parameters"],
                FileGenerator(self.subprocess),
                hive_config,
                sub_projects,
                "build"
        )

    def run(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        sub_projects = self._find_sub_projects(
                args["subprojects"],
                hive_config,
                "run"
        )
        self._execute_templated_command(
                "./run.sh",
                args["parameters"],
                FileGenerator(self.subprocess),
                hive_config,
                sub_projects,
                "run"
        )

    def kill(self, args):
        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        sub_projects = self._find_sub_projects(
                args["subprojects"],
                hive_config,
                "kill"
        )
        self._execute_templated_command(
                "./kill.sh",
                args["parameters"],
                FileGenerator(self.subprocess),
                hive_config,
                sub_projects,
                "kill"
        )

    # helpers
    def _find_sub_projects(self, asked_string, hive_config, action):

        asked_sub_projects = []
        for element in asked_string.split(","):
            if element in hive_config.execution_lists\
                    and action in hive_config.execution_lists[element]:
                asked_sub_projects = asked_sub_projects + hive_config.execution_lists[element][action]

            elif element in hive_config.sub_projects:
                asked_sub_projects = asked_sub_projects + [element]

            else:
                sys.exit(element + " is not recognised as an execution list or as a subproject")

        return asked_sub_projects

    def _execute_templated_command(self, command, cli_parameters, file_generator,
                                   hive_config, sub_projects, action):

        added_files = {}
        for sub_project in sub_projects:
            # update hive parameters on build folder
            added_files[sub_project] = file_generator.generate_hive_files(
                    hive_config=hive_config,
                    cli_parameters=cli_parameters,
                    file_path=hive_config.hive_config_path + "/" + sub_project + "/" + action
            )

        # execute command
        exception = None
        for sub_project in sub_projects:
            try:
                exception = self._execute_shell_command(
                        ["cd " + hive_config.hive_config_path + "/" + sub_project + "/" + action +
                         " && " + command]
                )

                if exception is not None:
                    break

            except OSError as error:
                print "Error on " + sub_project
                exception = error
                break

        # clean up
        for sub_project in sub_projects:
            file_generator.cleanup(
                    added_files[sub_project],
                    hive_config.hive_config_path + "/" + sub_project + "/" + action
            )

        if exception is not None:
            sys.exit(exception)

    def test(self, args):
        self.subprocess.call(["ls -la"], shell=True)
