import subprocess

from DockerVolume import DockerVolume


def get_docker_volumes():
    volumes_string = subprocess.check_output(["docker", "volume", "ls"]).split('\n')[1:-1]
    volumes = []
    for line in volumes_string:
        args = line.split()
        volumes.append(DockerVolume(args[0], args[1]))
    return volumes
