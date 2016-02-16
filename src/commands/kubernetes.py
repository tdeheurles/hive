import json
import os
import string
import sys
import time
import yaml

from gcloud import gcloud
from model.Command import Command
from model.KubernetesNamespace import KubernetesNamespace
from model.KubernetesPod import KubernetesPod
from model.ManifestFactory import ManifestFactory
from business.FileGenerator import FileGenerator


class kubernetes(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "kubernetes", subprocess, hive_home, options)

        self.resources_path = '/hive_share/kubernetes/manifests'
        self._cli = gcloud(subprocess, hive_home, options).get_container() + ["kubectl"]

    # commands
    def status(self, args):
        self._verbose("status")
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
        self._verbose("namespaces")
        self.subprocess.check_call(self._cli + ["get", "ns"])

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        self._execute_command(command)

    def create_environment(self, args):
        self._verbose("create_environment")
        manifest_factory = ManifestFactory()
        manifest = manifest_factory.new_namespace(args)
        output = json.dumps(manifest)
        self._create_resource(output, self.resources_path, '/namespace.json')

    def delete(self, args):
        self._verbose("delete")
        self._execute_command(["delete", "ns", args["name"]])

    def create(self, args):
        self._verbose("create")
        path = args["path"]
        parameters = args["parameters"]
        if len(parameters) % 2 != 0:
            sys.exit("parameters need to be key value pairs")

        with open(self.hive_home + path, 'r') as f:
            pattern = f.read()

        for i in range(0, len(parameters), 2):
            pattern = pattern.replace(parameters[i], parameters[i + 1])

        self._create_resource(pattern, self.resources_path, '/resource')

    def scale(self, args):
        self._verbose("scale")
        self._execute_command([
            "scale",
            "--namespace=" + args["namespace"],
            "--replicas=" + args["count"],
            "rc", args["service"]
        ])

    def test_tool(self, args):
        self._verbose("test_tools")
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
        self._verbose("deploy")
        build = args["build"]
        environment = args["environment"]

        deployment, templates_folder, configuration = self._read_files(args)

        self._control_deployment_strategy(args, deployment, environment)

        hive_file_transpiler = FileGenerator(self.subprocess)

        for kind in ["services", "replicationController"]:
            for resource in deployment[kind]:
                path = self.hive_home + "/" + templates_folder + "/" + resource["name"]
                self._deploy_create_resource(
                    kind, path, resource,
                    hive_file_transpiler,
                    configuration, build, environment
                )

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

    def _read_files(self, args):
        with open(self.hive_home + args["deployment_file"], 'r') as f:
            deployment = yaml.load(f.read())["spec"]
            configuration_file = deployment["configuration"]
            templates_folder = deployment["templates"]

        with open(self.hive_home + "/" + configuration_file, 'r') as f:
            configuration = yaml.load(f.read())["spec"]

        return deployment, templates_folder, configuration

    def _deploy_create_resource(self, kind, path, resource, hive_file_transpiler, configuration, build, environment):
        hive_file_transpiler.generate_hive_files(
            configuration,
            ["build", build],
            path
        )

        kind_short_name = "svc" if kind == "services" else "rc"

        with open(path + "/" + kind_short_name + ".yml", "r") as f:
            template = yaml.load(f.read())

        template["metadata"]["namespace"] = environment

        # add public=true for services to expose
        if "services" == kind and "public" in resource:
            if "labels" not in template["metadata"]:
                template["metadata"]["labels"] = {}
            template["metadata"]["labels"]["public"] = "true"

        self._create_resource(
            json.dumps(template),
            self.resources_path,
            resource["name"] + kind_short_name
        )
        hive_file_transpiler.cleanup([kind_short_name + ".yml"], path)

    def _control_deployment_strategy(self, args, deployment, environment):
        if "deploymentStrategy" in deployment and deployment["deploymentStrategy"] == "Recreate":

            namespaces = KubernetesNamespace.namespaces_from_api_call(
                self.subprocess.check_output(self._cli + ["get", "ns"])
            )
            for namespace in namespaces:
                if namespace.name == environment:
                    self.delete({"name": environment})

            create_environment_args = {
                "name": environment,
                "project": deployment["project"]
            }

            if "subproject" in args:
                create_environment_args["subproject"] = args["subproject"]

            self.create_environment(create_environment_args)
