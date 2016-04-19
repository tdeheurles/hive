import sys

from model.Command import Command
from model.DockerVolume import DockerVolume
from model.DockerContainer import DockerContainer


class docker(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "docker", subprocess, hive_home, options)
        self._cli = ["docker"]

    # commands
    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        self._execute_command(command)

    def remove_working_directory(self, args):
        volume_to_search = "hive_working_directory"

        volumes = self.get_docker_volumes()
        volume_exist = len([volume for volume in volumes if volume.name == volume_to_search]) != 0

        if not volume_exist:
            print volume_to_search + " does not exist"
            return

        # Get information on all container
        containers = self.get_docker_containers()
        containers_to_remove = [container for container in containers if
                                len([mount for mount in container.mounts if mount.name == "hive_working_directory"])]

        print "Containers to remove: " + len(containers_to_remove)

        for container in containers_to_remove:
            if container.running:
                self.subprocess.check_output(["docker", "kill", container.id])

            self.subprocess.check_output(["docker", "rm", container.id])

        self.subprocess.check_output(["docker", "volume", "rm", "hive_working_directory"])
        print volume_to_search + " removed"

    # public
    def get_docker_volumes(self):
        volumes_string = self.subprocess.check_output(["docker", "volume", "ls"]).split('\n')[1:-1]
        volumes = []
        for line in volumes_string:
            args = line.split()
            volumes.append(DockerVolume.docker_volume_from_cli(args[0], args[1]))
        return volumes

    def get_docker_containers(self):
        container_ids = self.subprocess.check_output(["docker", "ps", "-aq"]).split('\n')[1:-1]
        containers = []
        for container_id in container_ids:
            json_details = self.subprocess.check_output(["docker", "inspect", container_id])
            containers.append(DockerContainer(json_details))
        return containers

    # helpers
    def _execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError as error:
            sys.exit(error)
