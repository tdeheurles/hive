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

        self.resources_path = '/hive_share/kubernetes/manifests'
        self._cli = gcloud(subprocess, hive_home, options).get_container() + " kubectl "

    # commands
    def status(self, args):
        self._verbose("status")
        namespace = "--namespace=" + args["namespace"]
        print "\n\033[92m==================== SERVICES ====================\n\033[0m"
        self.subprocess.check_call(self._cli + " get services " + namespace, shell=True)
        print "\n\033[92m======================= RC =======================\n\033[0m"
        self.subprocess.check_call(self._cli + " get rc " + namespace, shell=True)
        print "\n\033[92m====================== PODS ======================\n\033[0m"
        self.subprocess.check_call(self._cli + " get pods " + namespace, shell=True)
        print "\n\033[92m====================== NODES =====================\n\033[0m"
        self.subprocess.check_call(self._cli + " get nodes " + namespace, shell=True)

    def namespaces(self, args):
        self._verbose("namespaces")
        self.subprocess.check_call(self._cli + " get ns", shell=True)

    def cli(self, args):
        self._verbose("cli")
        command = args["parameters"] if "parameters" in args else []
        if isinstance(command, list):
            command = string.join(command)

        self._execute_command(command)

    def create_environment(self, args):
        self._verbose("create_environment")
        manifest_factory = ManifestFactory()
        manifest = manifest_factory.new_namespace(args)
        output = json.dumps(manifest)
        self._create_resource(output, self.resources_path, '/namespace.json')

    def delete(self, args):
        self._verbose("delete")
        self._execute_command("delete ns " + args["name"])

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
        # NEED TO UPDATE SERVICE TO SOMETHING EASIER TO SPELL: ie: PRICING should become PRICING-0-0-860
        self._verbose("scale")
        self._execute_command(
                "scale --namespace=" + args["namespace"] + \
                " --replicas=" + args["count"] + \
                " rc " + args["service"]
        )

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
                        "exec -ti --namespace=" + namespace + " " + pod.name + " bash"
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
                                hive_config, build, environment
                        )

                        # if deployment_strategy == "RollingUpdate":
                        #     # we rolling update replication controller
                        #     if "replicationController" in deployment:
                        #         for rc in [rcs["name"] for rcs in deployment["replicationController"]]:
                        #             self.rolling_update({
                        #                 "service": rc,
                        #                 "build": build,
                        #                 "environment": environment,
                        #                 "deployment_file": deployment_file
                        #             })

    # def rolling_update(self, args):
    #     self._verbose("rolling_update")
    #
    #     service = args["service"]
    #     build = args["build"]
    #     environment = args["environment"]
    #     deployment_file = args["deployment_file"]
    #     deployment, templates_folder, configuration_file = self._read_files(deployment_file)
    #     path_to_resource = self.hive_home + "/" + templates_folder + "/" + service
    #
    #     file_transpiler = FileGenerator(self.subprocess)
    #     added_files = file_transpiler.generate_hive_files(
    #             configuration_file,
    #             ["build", build],
    #             path_to_resource
    #     )
    #
    #     with open(path_to_resource + "/" + added_files[0], "r") as stream:
    #         template = yaml.load(stream.read())
    #
    #     template["metadata"]["namespace"] = environment
    #
    #     if not os.path.exists(self.resources_path):
    #         os.makedirs(self.resources_path)
    #
    #     resource_to_update = self.resources_path + "/" + service
    #     with open(resource_to_update, 'w') as f:
    #         f.write(json.dumps(template))
    #
    #     error = None
    #     try:
    #         self.subprocess.call(
    #                 self._cli + \
    #                 " rolling-update " + service + \
    #                 " --namespace=" + environment + \
    #                 " -f ", resource_to_update,
    #                 shell=True
    #         )
    #
    #     except OSError as osError:
    #         error = osError
    #
    #     file_transpiler.cleanup(added_files, path_to_resource)
    #
    #     if error is not None:
    #         sys.exit(error)

    # helpers
    def _get_pods_by_name(self, name, namespace):
        call = self._get_pods(namespace)
        kubernetes_pods = KubernetesPod.pods_from_api_call(call)
        return [pod for pod in kubernetes_pods
                if string.find(pod.name, name) is not -1]

    def _get_pods(self, namespace):
        return self.subprocess.check_output(
                self._cli + "get pods --namespace=" + namespace,
                shell=True
        )

    def _start_testtool(self, namespace):
        with open("commands/templates/testtool-pod.yml", 'r') as stream:
            testtool_pod = yaml.load(stream)

        testtool_pod["metadata"]["namespace"] = namespace

        self._create_resource(
                json.dumps(testtool_pod), '/hive_share/kubernetes/pods', namespace + '-testtool.json'
        )

    def _create_resource(self, output, path, file_name):
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + "/" + file_name, 'w') as f:
            f.write(output)

        self._execute_command("create -f " + path + "/" + file_name)

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
            self.subprocess.check_call(
                    "cd " + self.hive_home + " && " + self._cli + " " + command,
                    shell=True
            )
        except self.subprocess.CalledProcessError as error:
            sys.exit(error)

    def _deploy_create_resource(self, kind, sub_project, hive_file_transpiler,
                                hive_config, build, environment):

        hive_file_transpiler.generate_hive_files(
                hive_config,
                ["id", build],
                sub_project.path + "/kubernetes"
        )

        kind_short_name = self._kind_shot_name(kind)

        with open(sub_project.path + "/kubernetes/" + kind_short_name + ".yml", "r") as stream:
            template = yaml.load(stream.read())

        template["metadata"]["namespace"] = environment

        self._create_resource(
                json.dumps(template),
                self.resources_path,
                kind_short_name + ".yml"
        )
        hive_file_transpiler.cleanup([kind_short_name + ".yml"], sub_project.path + "/kubernetes")

    def _control_deployment_strategy(self, args, hive_file, environment):
        deployment_strategy = "Recreate"
        if "deploymentStrategy" in hive_file.kubernetes:
            deployment_strategy = hive_file.kubernetes["deploymentStrategy"]

        if deployment_strategy == "Recreate":
            namespaces = KubernetesNamespace.namespaces_from_api_call(
                    self.subprocess.check_output(self._cli + " get ns", shell=True)
            )
            for namespace in namespaces:
                if namespace.name == environment:
                    print "\n=================="
                    self.delete({"name": environment})
                    print "Giving time for namespace to be completely removed ..."
                    time.sleep(5)

            create_environment_args = {
                "name": environment,
                "project": hive_file.configuration["project"]
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
