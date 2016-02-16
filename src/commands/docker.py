import sys

from model.Command import Command
from model.DockerVolume import DockerVolume


class docker(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "docker", subprocess, hive_home, options)
        self._cli = ["docker"]

    # commands
    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        self._execute_command(command)

    # public
    def get_docker_volumes(self):
        volumes_string = self.subprocess.check_output(["docker", "volume", "ls"]).split('\n')[1:-1]
        volumes = []
        for line in volumes_string:
            args = line.split()
            volumes.append(DockerVolume(args[0], args[1]))
        return volumes

    # helpers
    def _execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError as error:
            sys.exit(error)
