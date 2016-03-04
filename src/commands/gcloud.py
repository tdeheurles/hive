import sys
import string

from model.Command import Command
from model.GcloudInstanceGroup import GcloudInstanceGroup


class gcloud(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "gcloud", subprocess, hive_home, options)

        self.container = \
            "docker run -ti " + \
            "-v hive_cache_gcloud:/root/.config " + \
            "-v hive_cache_kube:/root/.kube " + \
            "-v hive_share:/hive_share " + \
            "-v kubernetes_credentials:/kubernetes_credentials" + \
            "-v ${PWD}:${PWD} " + \
            "-w ${PWD} " + \
            "weareadaptive/gcloud:1.0 "

        self._cli = self.container + "gcloud "

    # commands
    def init(self, args):
        self._verbose("init")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_gcloud"])
        self.subprocess.check_call(self._cli + "init", shell=True)

    def credentials(self, args):
        self._verbose("credentials")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_kube"])
        self.subprocess.check_call(
                self._cli + "container clusters get-credentials " + args["cluster"],
                shell=True
        )

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        try:
            self.subprocess.check_call(self._cli + string.join(command), shell=True)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    def show(self, args):
        self._verbose("show")
        self.subprocess.call(self._cli + "compute machine-types list", shell=True)

    def create_cluster(self, args):
        self._verbose("create_cluster")

        quantity = "1"
        if "quantity" in args:
            quantity = args["quantity"]

        try:
            print "create command can take a few seconds ..."
            self.subprocess.call(
                    self._cli + \
                    "container clusters create " + args["name"] + \
                    " --zone " + args["zone"] + \
                    " --machine-type " + args["type"] + \
                    " --num-nodes " + quantity,
                    shell=True
            )
        except OSError:
            sys.exit(1)

    def autoscale(self, args):
        self._verbose("update_cluster")

        instance_group = self._get_instance_group(args["name"])

        try:
            print "autoscale command can take a few seconds ..."
            self.subprocess.call(
                    self._cli + \
                    "compute instance-groups managed set-autoscaling " + \
                    instance_group.name + \
                    " --zone " + instance_group.zone + \
                    " --max-num-replicas " + args["max"] + \
                    " --target-cpu-utilization " + args["target"] + \
                    " --cool-down-period " + args["cd"],
                    shell=True
            )
        except OSError as error:
            sys.exit(error)

    def _get_instance_group(self, cluster_name):
        # get group name by using cluster name
        try:
            instance_group_call = self.subprocess.check_output(
                    self._cli + "compute instance-groups managed list", shell=True
            )
        except OSError as error:
            sys.exit(error)
        instance_groups = GcloudInstanceGroup.instance_group_from_api_call(
                instance_group_call
        )
        filter_instance_groups = [instance_group for instance_group
                                  in instance_groups if cluster_name in instance_group.name]
        if len(filter_instance_groups) is not 1:
            print "error while finding the cluster group by using cluster name"
            sys.exit(1)
        instance_group = filter_instance_groups[0]
        return instance_group

    def delete(self, args):
        instance_group = self._get_instance_group(args["name"])

        try:
            self.subprocess.check_call(
                    self._cli + "container clusters delete --quiet " + args["name"] + " --zone " + instance_group.zone,
                    shell=True
            )
        except OSError as error:
            sys.exit(error)

    # public
    def get_container(self):
        # docker_instance = docker(self.subprocess, self.hive_home, self.options)
        # volumes = [volume.name for volume in docker_instance.get_docker_volumes()]

        # if "hive_cache_gcloud" not in volumes:
        #     print """

        #     ===================================
        #     You need to login with gcloud first
        #     ===================================

        #     try with: ./hive gcloud init
        #     """
        #     sys.exit("Bad gcloud init")

        # if "hive_cache_kube" not in volumes:
        #     print """

        #     ===============================================
        #     You need to get the credentials of your cluster
        #     ===============================================

        #     try with: ./hive gcloud credentials CLUSTER_NAME
        #     """
        #     sys.exit("Bad cluster credentials")
        # else:
        return self.container
