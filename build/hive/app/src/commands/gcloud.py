import sys
from docker import docker
from Command import Command


class gcloud(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "gcloud", subprocess, hive_home, options)

        self.container = [
            "docker", "run", "-ti",
            "-v", "hive_cache_gcloud:/root/.config",
            "-v", "hive_cache_kube:/root/.kube",
            "-v", "hive_share:/hive_share",
            "weareadaptive/gcloud:1.0"
        ]
        self._cli = self.container + ["gcloud"]

    # commands
    def init(self, args):
        self._verbose("init")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_gcloud"])
        self.subprocess.check_call(self._cli + ["init"])

    def credentials(self, args):
        self._verbose("credentials")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_kube"])
        self.subprocess.check_call(
            self._cli + ["container", "clusters", "get-credentials", args["cluster"]]
        )

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    # public
    def get_container(self):
        docker_instance = docker(self.subprocess, self.hive_home, self.options)
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
