from model.Command import Command
from kubernetes import kubernetes


class local_cluster(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "kubernetes", subprocess, hive_home, options)

        self._kubernetes = kubernetes(subprocess, hive_home, options)

    # KUBERNETES
    def create(self, args):
        docker_host = args["docker_host"]

        kube_version = "v1.2.0"
        if "version" in args:
            kube_version = args["version"]

        apiserver_port = "8080"
        if "port" in args:
            apiserver_port = args["port"]

        self._start_master(kube_version, apiserver_port)
        self._set_context(apiserver_port, docker_host)

    def _start_master(self, kube_version, apiserver_port):
        master_template = """
            docker run \
                -d \
                --net=host \
                --pid=host \
                --privileged \
                --restart=on-failure \
                -v /sys:/sys:ro \
                -v /var/run:/var/run:rw \
                -v /var/lib/docker/:/var/lib/docker:rw \
                -v /var/lib/kubelet/:/var/lib/kubelet:shared \
                tdeheurles/kubernetes:__KUBE_VERSION__ \
                  /start.sh \
                    --port __APISERVER_PORT__
        """
        master_command = master_template\
            .replace("__KUBE_VERSION__", kube_version)\
            .replace("__APISERVER_PORT__", apiserver_port)

        self.subprocess.call(master_command, shell=True)

    def _set_context(self, apiserver_port, docker_host):
        print "Setting local kubernetes as kubectl context"
        self.subprocess.call(
                self._kubernetes.kubectl + " config set-cluster dev --server=" +
                "http://" + docker_host + ":" + apiserver_port,
                shell=True
        )
        self.subprocess.call(
                self._kubernetes.kubectl + " config set-context dev " +
                " --user=dev " +
                " --cluster=dev",
                shell=True
        )
        self.subprocess.call(
                self._kubernetes.kubectl + " config use-context dev",
                shell=True
        )

    # ADDONS
    def start_addons(self, args):
        apiserver_port = "8080"
        if "port" in args:
            apiserver_port = args["port"]

        self._start_dns(apiserver_port)
        self._start_dashboard()

    def _start_dns(self, apiserver_port):
        import yaml
        import json

        with open("./commands/templates/local_cluster/dns-svc.yml") as stream:
            dns_svc_template_content = stream.read()

        with open("./commands/templates/local_cluster/dns-rc.yml") as stream:
            dns_rc_template_content = stream.read() \
                .replace("__APISERVER_PORT__", apiserver_port)

        for content in [dns_svc_template_content, dns_rc_template_content]:
            template = yaml.load(content)
            template["metadata"]["namespace"] = "default"

            self._kubernetes.create_resource(
                    json.dumps(template),
                    self._kubernetes.resources_path,
                    "resource.yml"
            )

    def _start_dashboard(self):
        import yaml
        import json

        with open("./commands/templates/local_cluster/dashboard-svc.yml") as stream:
            svc_template_content = stream.read()

        with open("./commands/templates/local_cluster/dashboard-rc.yml") as stream:
            rc_template_content = stream.read()

        for content in [svc_template_content, rc_template_content]:
            template = yaml.load(content)
            template["metadata"]["namespace"] = "default"

            self._kubernetes.create_resource(
                    json.dumps(template),
                    self._kubernetes.resources_path,
                    "resource.yml"
            )

    # PROXY
    def proxy(self, args):
        proxy_command_template = """
            docker run \
                -d \
                --net=host \
                tdeheurles/proxy:0.0 \
                    /start.sh \
                    --host-port=__HOST_PORT__ \
                    --container-port=__CONTAINER_PORT__ \
                    --service=__SERVICE__ \
                    --namespace=__NAMESPACE__ \
                    --method=__METHOD__
        """

        proxy_command = proxy_command_template\
            .replace("__HOST_PORT__", args["hostport"])\
            .replace("__CONTAINER_PORT__", args["containerport"])\
            .replace("__SERVICE__", args["serviceip"])\
            .replace("__NAMESPACE__", "useless-for-now")\
            .replace("__METHOD__", args["method"])

        self.subprocess.call(proxy_command, shell=True)
