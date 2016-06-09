import sys
import string

from model.Command import Command
from model.GcloudInstanceGroup import GcloudInstanceGroup


class gcloud(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "gcloud", subprocess, hive_home, options)

    # commands
    def init(self, args):
        self._verbose("init")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_gcloud"])
        self.subprocess.check_call(self._get_cli(args) + "init", shell=True)

    def set_cluster(self, args):
        self._verbose("credentials")
        self.subprocess.check_call(["docker", "volume", "create", "--name=hive_cache_kube"])
        self.subprocess.check_call(
                self._get_cli(args) + "container clusters get-credentials " + args["cluster"],
                shell=True
        )

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        try:
            self.subprocess.check_call(self._get_cli(args) + string.join(command), shell=True)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    def show(self, args):
        self._verbose("show")
        self.subprocess.call(self._get_cli(args) + "compute machine-types list", shell=True)

    def create_cluster(self, args):
        self._verbose("create_cluster")

        quantity = "1"
        if "quantity" in args:
            quantity = args["quantity"]

        try:
            print "create command can take a few seconds ..."
            self.subprocess.call(
                    self._get_cli(args) + \
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

        instance_group = self._get_instance_group(args)

        try:
            print "autoscale command can take a few seconds ..."
            self.subprocess.call(
                    self._get_cli(args) + \
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

    def _get_instance_group(self, args):
        # get group name by using cluster name
        try:
            instance_group_call = self.subprocess.check_output(
                    self._get_cli(args) + "compute instance-groups managed list", shell=True
            )
        except OSError as error:
            sys.exit(error)
        instance_groups = GcloudInstanceGroup.instance_group_from_api_call(
                instance_group_call
        )
        filter_instance_groups = [instance_group for instance_group
                                  in instance_groups if args["name"] in instance_group.name]
        if len(filter_instance_groups) is not 1:
            print "error while finding the cluster group by using cluster name"
            sys.exit(1)
        instance_group = filter_instance_groups[0]
        return instance_group

    def delete(self, args):
        instance_group = self._get_instance_group(args["name"])

        try:
            self.subprocess.check_call(
                    self._get_cli(args) + "container clusters delete --quiet " + args["name"] + " --zone " + instance_group.zone,
                    shell=True
            )
        except OSError as error:
            sys.exit(error)

    # public
    def get_container(self, args):

        TTY = "" if 'notty' in args else "-ti "

        self.container = \
            "docker run " + TTY + \
            "-v hive_cache_gcloud:/root/.config " + \
            "-v hive_cache_kube:/root/.kube " + \
            "-v hive_share:/hive_share " + \
            "-v ${PWD}:${PWD} " + \
            "-w ${PWD} " + \
            "weareadaptive/gcloud:1.1 "

        return self.container

    def _get_cli(self, args):
        return self.get_container(args) + " gcloud "
