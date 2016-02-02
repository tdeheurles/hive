import sys
from DockerVolume import DockerVolume


class docker:
    def __init__(self, subprocess):
        self.subprocess = subprocess
        self._cli = ["docker"]

    def execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    def cli(self, args):
        command = args["parameters"] if "parameters" in args else []
        self.execute_command(command)

    def get_docker_volumes(self):
        volumes_string = self.subprocess.check_output(["docker", "volume", "ls"]).split('\n')[1:-1]
        volumes = []
        for line in volumes_string:
            args = line.split()
            volumes.append(DockerVolume(args[0], args[1]))
        return volumes
