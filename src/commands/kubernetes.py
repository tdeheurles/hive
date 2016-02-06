import time
import sys
import os
import string
import yaml
import json
from script import script
from gcloud import gcloud
from ManifestFactory import ManifestFactory
from KubernetesPod import KubernetesPod


class kubernetes:
    def __init__(self, subprocess):
        self.resources_path = '/hive_share/kubernetes/manifests'
        self.subprocess = subprocess
        self._cli = gcloud(subprocess).get_container() + ["kubectl"]

    # commands
    def status(self, args):
        namespace = "--namespace=" + args["namespace"]
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

    def namespaces(self, args):
        self.subprocess.check_call(self._cli + ["get", "ns"])

    def cli(self, args):
        command = args["parameters"] if "parameters" in args else []
        self._execute_command(command)

    def create_environment(self, args):
        manifest_factory = ManifestFactory()
        manifest = manifest_factory.new_namespace(args)
        output = json.dumps(manifest)
        self._create_resource(output, self.resources_path, '/namespace.json')

    def delete(self, args):
        self._execute_command(["delete", "ns", args["name"]])

    def create(self, args):
        path = args["path"]
        parameters = args["parameters"]
        if len(parameters) % 2 != 0:
            sys.exit("parameters need to be key value pairs")

        with open("/currentFolder/" + path, 'r') as f:
            pattern = f.read()

        for i in range(0, len(parameters), 2):
            pattern = pattern.replace(parameters[i], parameters[i + 1])

        self._create_resource(pattern, self.resources_path, '/resource')

    def scale(self, args):
        self._execute_command([
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
                self._execute_command(
                    ["exec", "-ti", "--namespace=" + namespace, pod.name, "bash"]
                )
            else:
                sys.exit("failed to connect to a testtool pod")
        else:
            sys.exit("failed to connect to a testtool pod")

    def deploy(self, args):
        def create_environment():
            create_environment_args = {"name": environment, "project": deployment["project"]}
            if "subproject" in args:
                create_environment_args["subproject"] = args["subproject"]
            self.create_environment(create_environment_args)

        def read_files():
            with open("/currentFolder/" + args["deployment_file"], 'r') as f:
                # initial deployment is the file with the hive variable in it
                dep = yaml.load(f.read())["spec"]
                configuration_file = dep["configuration"]
                folder = dep["templates"]
            with open("/currentFolder/" + configuration_file, 'r') as f:
                conf = yaml.load(f.read())["spec"]
            return dep, folder, conf

        build = args["build"]
        environment = args["environment"]

        deployment, templates_folder, configuration = read_files()

        create_environment()

        hive_file_transpiler = script(None)

        # services
        for service_name in [svc["name"] for svc in deployment["services"]]:
            hive_file_transpiler.generate_hive_files(
                configuration,
                ["build", build],
                "/currentFolder/" + templates_folder + "/" + service_name
            )

        for service in deployment["services"]:
            path = "/currentFolder/" + templates_folder + "/" + service["name"]
            with open(path + "/" + "svc.yml", "r") as f:
                template = yaml.load(f.read())

            # add namespace
            template["metadata"]["namespace"] = environment

            # add public=true for nsgate
            if "public" in service:
                if "labels" not in template["metadata"]:
                    template["metadata"]["labels"] = {}
                template["metadata"]["labels"]["public"] = "true"

            self._create_resource(
                json.dumps(template),
                self.resources_path,
                service["name"] + "svc"
            )
            hive_file_transpiler.cleanup(["svc.yml"], path)

        # replication controller
        for rc_name in [rc["name"] for rc in deployment["replicationController"]]:
            hive_file_transpiler.generate_hive_files(
                configuration,
                ["build", build],
                "/currentFolder/" + templates_folder + "/" + rc_name
            )

        for rc in deployment["replicationController"]:
            path = "/currentFolder/" + templates_folder + "/" + rc["name"]
            with open(path + "/" + "rc.yml", "r") as f:
                template = yaml.load(f.read())

            # add namespace
            template["metadata"]["namespace"] = environment

            self._create_resource(
                json.dumps(template),
                self.resources_path,
                rc["name"] + "rc"
            )
            hive_file_transpiler.cleanup(["rc.yml"], path)

    # helpers
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

    def _create_resource(self, output, path, file_name):
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + file_name, 'w') as f:
            f.write(output)

        self._execute_command(["create", "-f", path + file_name])

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

    def _execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError as error:
            sys.exit(1)
