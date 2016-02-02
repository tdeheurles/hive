import sys
import os
from gcloud import gcloud
from ManifestFactory import ManifestFactory
import json

class kubernetes:
    def __init__(self, subprocess):
        self.subprocess = subprocess
        self._cli = gcloud(subprocess).get_container() + ["kubectl"]

    def status(self, parameters):
        namespace = "--namespace=" + parameters["namespace"]
        print "\n\033[92mSERVICES\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "services", namespace])
        print "\n\033[92mRC\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "rc", namespace])
        print "\n\033[92mPODS\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "pods", namespace])
        print "\n\033[92mENDPOINTS\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "endpoints", namespace])
        print "\n\033[92mINGRESS\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "ingress", namespace])
        print "\n\033[92mNODES\n\033[0m"
        self.subprocess.check_call(self._cli + ["get", "nodes", namespace])

    def execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    def namespaces(self, args):
        self.subprocess.check_call(self._cli + ["get", "ns"])

    def cli(self, args):
        command = args["parameters"] if "parameters" in args else []
        self.execute_command(command)

    def create_environment(self, args):
        manifest_factory = ManifestFactory()
        manifest = manifest_factory.new_namespace(args)
        output = json.dumps(manifest)

        path = '/hive_share/kubernetes'
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + '/namespace.yml', 'w') as f:
            f.write(output)

        self.execute_command(["create", "-f", path + "/namespace.yml"])

    def delete(self, args):
        self.execute_command(["delete", "ns", args["name"]])

    def scale(self, args):
        print args
        self.execute_command([
            "scale",
            "--namespace=" + args["namespace"],
            "--replicas=" + args["count"],
            "rc", args["service"]
        ])
        #./kubectl scale --namespace=$namespace --replicas=$count rc $service
