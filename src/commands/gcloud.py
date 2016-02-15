import sys

from docker import docker
from modele.Command import Command
from modele.GcloudInstanceGroup import GcloudInstanceGroup


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

    def show(self, args):
        self._verbose("show")
        self.subprocess.call(self._cli + ["compute", "machine-types", "list"])

    def create_cluster(self, args):
        self._verbose("create_cluster")

        quantity = "1"
        if "quantity" in args:
            quantity = args["quantity"]

        try:
            print "create command can take a few seconds ..."
            self.subprocess.call(
                self._cli + [
                    "container", "clusters", "create", args["name"],
                    "--zone",         args["zone"],
                    "--machine-type", args["type"],
                    "--num-nodes",    quantity]
                )
        except OSError:
            sys.exit(1)

    def autoscale(self, args):
        self._verbose("update_cluster")

        # get group name by using cluster name
        try:
            instance_group_call = self.subprocess.check_output(
                self._cli + ["compute", "instance-groups", "managed", "list"]
            )
        except OSError as error:
            sys.exit(error)

        instance_groups = GcloudInstanceGroup.instance_group_from_api_call(
                instance_group_call
        )

        instance_group_names = [instance_group.name for instance_group
                                in instance_groups if args["name"] in instance_group.name]

        if len(instance_group_names) is not 1:
            print "error while finding the cluster group by using cluster name"
            sys.exit(1)

        try:
            print "autoscale command can take a few seconds ..."
            self.subprocess.call(
                self._cli + [
                    "compute", "instance-groups", "managed", "set-autoscaling",
                    instance_group_names[0],
                    "--max-num-replicas",       args["max"],
                    "--target-cpu-utilization", args["target"],
                    "--cool-down-period",       args["cd"]]
            )
        except OSError as error:
            sys.exit(error)

    def delete(self, args):
        try:
            self.subprocess.check_call(
                self._cli + ["container", "clusters", "delete",
                             "--quiet", args["name"]]
            )
        except OSError as error:
            sys.exit(error)

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
