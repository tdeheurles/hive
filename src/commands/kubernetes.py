import time
import sys
import os
import string
import yaml
import json
from gcloud import gcloud
from ManifestFactory import ManifestFactory
from KubernetesPod import KubernetesPod


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
        self._create_resource(manifest, '/hive_share/kubernetes/namespaces', '/namespace.json')

    def delete(self, args):
        self.execute_command(["delete", "ns", args["name"]])

    def scale(self, args):
        self.execute_command([
            "scale",
            "--namespace=" + args["namespace"],
            "--replicas=" + args["count"],
            "rc", args["service"]
        ])

    def test_tool(self, args):
        namespace = args["namespace"]

        testtool_pods = []
        attempt = 0
        while attempt < 10:
            testtool_pods = self._get_pods_by_name("testtool", namespace)
            if len(testtool_pods) != 0:
                break
            self._start_testtool(namespace)
            time.sleep(1)
            attempt += 1

        if len(testtool_pods) != 0:
            pod = testtool_pods[0]

            result = self._wait_for_pod_to_run(pod, namespace)

            if result == 0:
                self.execute_command(
                    ["exec", "-ti", "--namespace=" + namespace, pod.name, "bash"]
                )
            else:
                sys.exit("failed to connect to a testtool pod")
        else:
            sys.exit("failed to connect to a testtool pod")

    def _get_pods_by_name(self, name, namespace):
        call = self._get_pods(namespace)
        kubernetes_pods = KubernetesPod.pods_from_api_call(call)
        return [pod for pod in kubernetes_pods
                if string.find(pod.name, name) is not -1]

    def _get_pods(self, namespace):
        return self.subprocess.check_output(
            self._cli + ["get", "pods", "--namespace=" + namespace]
        )

    def _start_testtool(self, namespace):
        with open("commands/templates/testtool-pod.yml", 'r') as stream:
            testtool_pod = yaml.load(stream)

        testtool_pod["metadata"]["namespace"] = namespace

        self._create_resource(
            testtool_pod, '/hive_share/kubernetes/pods', '/' + namespace + '-testtool.json'
        )

    def _create_resource(self, manifest, path, file_name):
        output = json.dumps(manifest)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + file_name, 'w') as f:
            f.write(output)

        self.execute_command(["create", "-f", path + file_name])

    def _wait_for_pod_to_run(self, origin_pod, namespace):
        attempt = 0
        while attempt < 10:
            pods = self._get_pods_by_name(origin_pod.name, namespace)
            status = [pod.status for pod in pods]
            if len(status) < 1:
                sys.exit("the pod " + origin_pod.name + "does not exist")

            if status[0] == "Running":
                return 0
            else:
                print "pod status is " + status[0] + ", waiting ..."

            time.sleep(5)
            attempt += 1
        return 1
