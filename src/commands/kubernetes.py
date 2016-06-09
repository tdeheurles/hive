import pprint
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
from model.HiveConfigFactory import HiveConfigFactory


class kubernetes(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "kubernetes", subprocess, hive_home, options)

        self.gcloud = gcloud(subprocess, hive_home, options)
        self.resources_path = '/hive_share/kubernetes/manifests'

    # commands
    def status(self, args):
        self._verbose("status")
        namespace = "--namespace=" + args["namespace"]
        print "\n\033[92m==================== SERVICES ====================\n\033[0m"
        self.subprocess.check_call(self._get_kubectl(args) + " get services " + namespace, shell=True)
        print "\n\033[92m======================= RC =======================\n\033[0m"
        self.subprocess.check_call(self._get_kubectl(args) + " get rc " + namespace, shell=True)
        print "\n\033[92m====================== PODS ======================\n\033[0m"
        self.subprocess.check_call(self._get_kubectl(args) + " get pods " + namespace, shell=True)
        print "\n\033[92m====================== NODES =====================\n\033[0m"
        self.subprocess.check_call(self._get_kubectl(args) + " get nodes " + namespace, shell=True)

    def namespaces(self, args):
        self._verbose("namespaces")
        self.subprocess.check_call(self._get_kubectl(args) + " get ns", shell=True)

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        if isinstance(command, list):
            command = string.join(command)

        self._execute_command(command, args)

    def create_environment(self, args):
        self._verbose("create_environment")
        manifest_factory = ManifestFactory()
        manifest = manifest_factory.new_namespace(args)
        output = json.dumps(manifest)
        self.create_resource(output, self.resources_path, '/namespace.json', args)

    def delete(self, args):
        self._verbose("delete")
        self._execute_command("delete ns " + args["name"], args)

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

        self.create_resource(pattern, self.resources_path, '/resource', args)

    def scale(self, args):
        # NEED TO UPDATE SERVICE TO SOMETHING EASIER TO SPELL: ie: PRICING should become PRICING-0-0-860
        self._verbose("scale")
        self._execute_command(
                "scale --namespace=" + args["namespace"] + \
                " --replicas=" + args["count"] + \
                " rc " + args["service"], args
        )

    def testtools(self, args):
        self._verbose("test_tools")
        namespace = args["namespace"]

        testtool_pods = []
        attempt = 0
        while attempt < 10:
            testtool_pods = self._get_pods_by_name("testtool", namespace, args)
            if len(testtool_pods) != 0:
                break
            self._start_testtool(namespace, args)
            time.sleep(1)
            attempt += 1

        if len(testtool_pods) != 0:
            pod = testtool_pods[0]

            result = self._wait_for_pod_to_run(pod, namespace, args)

            if result == 0:
                self._execute_command(
                        "exec -ti --namespace=" + namespace + " " + pod.name + " bash", args
                )
            else:
                sys.exit("failed to connect to a testtool pod")
        else:
            sys.exit("failed to connect to a testtool pod")

    def deploy(self, args):
        self._verbose("deploy")

        hive_config = HiveConfigFactory.create(
                self.hive_home + "/" + args["hive_file"]
        )

        build = args["build"]
        environment = args["environment"]
        deployment_strategy = self._control_deployment_strategy(args, hive_config, environment)

        file_transpiler = FileGenerator(self.subprocess)

        if deployment_strategy == "Recreate":
            # we delete everything and recreate
            kubernetes_sub_projects = hive_config.kubernetes_sub_projects()
            for kind in ["service", "secret", "replicationController"]:
                first = True
                for sub_project in kubernetes_sub_projects:
                    if kind in sub_project.kubernetes:
                        if first:
                            first = False
                            print "\n=================="

                        self._deploy_create_resource(
                                kind, sub_project,
                                file_transpiler,
                                hive_config, build, environment, args
                        )

    # helpers
    def _get_pods_by_name(self, name, namespace, args):
        call = self._get_pods(namespace, args)
        kubernetes_pods = KubernetesPod.pods_from_api_call(call)
        return [pod for pod in kubernetes_pods
                if string.find(pod.name, name) is not -1]

    def _get_pods(self, namespace, args):
        return self.subprocess.check_output(
                self._get_kubectl(args) + "get pods --namespace=" + namespace,
                shell=True
        )

    def _start_testtool(self, namespace, args):
        with open("commands/templates/testtool-pod.yml", 'r') as stream:
            testtool_pod = yaml.load(stream)

        testtool_pod["metadata"]["namespace"] = namespace

        self.create_resource(
                json.dumps(testtool_pod), '/hive_share/kubernetes/pods', namespace + '-testtool.json', args
        )

    def create_resource(self, output, path, file_name, args):
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + "/" + file_name, 'w') as f:
            f.write(output)

        self._execute_command("create -f " + path + "/" + file_name, args)

    def _wait_for_pod_to_run(self, origin_pod, namespace, args):
        attempt = 0
        while attempt < 10:
            pods = self._get_pods_by_name(origin_pod.name, namespace, args)
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

    def _execute_command(self, command, args):
        try:
            self.subprocess.check_call(
                    "cd " + self.hive_home + " && " + self._get_kubectl(args) + " " + command,
                    shell=True
            )
        except self.subprocess.CalledProcessError as error:
            sys.exit(error)

    def _deploy_create_resource(self, kind, sub_project, hive_file_transpiler,
                                hive_config, build, environment, args):

        hive_file_transpiler.generate_hive_files(
                hive_config,
                ["id", build],
                sub_project.path + "/kubernetes"
        )

        kind_short_name = self._kind_shot_name(kind)

        with open(sub_project.path + "/kubernetes/" + kind_short_name + ".yml", "r") as stream:
            template = yaml.load(stream.read())

        template["metadata"]["namespace"] = environment

        self.create_resource(
                json.dumps(template),
                self.resources_path,
                kind_short_name + ".yml", args
        )
        hive_file_transpiler.cleanup([kind_short_name + ".yml"], sub_project.path + "/kubernetes")

    def _control_deployment_strategy(self, args, hive_file, environment):
        deployment_strategy = "Recreate"
        if "deploymentStrategy" in hive_file.kubernetes:
            deployment_strategy = hive_file.kubernetes["deploymentStrategy"]

        if deployment_strategy == "Recreate":
            namespaces = KubernetesNamespace.namespaces_from_api_call(
                    self.subprocess.check_output(self._get_kubectl(args) + " get ns", shell=True)
            )
            for namespace in namespaces:
                if namespace.name == environment:
                    print "\n=================="
                    self.delete({"name": environment})
                    print "Giving time for namespace to be completely removed ..."
                    time.sleep(5)

            create_environment_args = {
                "name": environment,
                "project": hive_file.configuration["project"],
                "notty": args["notty"]
            }

            # if "subproject" in args:
            #     create_environment_args["subproject"] = args["subproject"]

            self.create_environment(create_environment_args)

        return deployment_strategy

    def _kind_shot_name(self, kind):
        if kind == "replicationController":
            return "rc"
        if kind == "service":
            return "svc"
        if kind == "secret":
            return "sct"

    def _get_kubectl(self, args):
        return self.gcloud.get_container(args) + " kubectl "