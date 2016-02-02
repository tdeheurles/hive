import sys
from docker import docker


class gcloud:
    def __init__(self, subprocess):
        self.container = [
            "docker", "run", "-ti",
            "-v", "hive_cache_gcloud:/root/.config",
            "-v", "hive_cache_kube:/root/.kube",
            "-v", "hive_share:/hive_share",
            "weareadaptive/gcloud:1.0"
        ]
        self._cli = self.container + ["gcloud"]
        self.subprocess = subprocess

    def init(self, parameters):
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_gcloud"])
        self.subprocess.check_call(self._cli + ["init"])

    def credentials(self, parameters):
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_kube"])
        self.subprocess.check_call(
            self._cli + ["container", "clusters", "get-credentials", parameters["cluster"]]
        )

    def get_container(self):
        docker_instance = docker(self.subprocess)
        volumes = [volume.name for volume in docker_instance.get_docker_volumes()]

        if "hive_cache_gcloud" not in volumes:
            print """

            ===================================
            You need to login with gcloud first
            ===================================

            try with: ./hive gcloud init
            """
            sys.exit("Bad gcloud init")

        if "hive_cache_kube" not in volumes:
            print """

            ===============================================
            You need to get the credentials of your cluster
            ===============================================

            try with: ./hive gcloud credentials CLUSTER_NAME
            """
            sys.exit("Bad cluster credentials")
        else:
            return self.container

    def cli(self, parameters):
        command = parameters["parameters"] if "parameters" in parameters else []
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

