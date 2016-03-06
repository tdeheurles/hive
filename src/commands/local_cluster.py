from model.Command import Command
from kubernetes import kubernetes


class local_cluster(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "kubernetes", subprocess, hive_home, options)

        self._dns_server_ip = "10.0.0.10"
        self._dns_domain = "cluster.local"
        self._kube_server_url = "http://192.168.99.100:8080"

        self._kubernetes = kubernetes(subprocess, hive_home, options)

    def create(self, args):
        kube_version = "v1.1.8"
        if "version" in args:
            kube_version = args["version"]

        etcd_command = """
        docker run -d                           \
            --net=host                          \
            gcr.io/google_containers/etcd:2.2.1 \
                /usr/local/bin/etcd             \
                    --addr=127.0.0.1:4001       \
                    --bind-addr=0.0.0.0:4001    \
                    --data-dir=/var/etcd/data
        """

        kubernetes_command_template = """
        docker run -d                                           \
            --net=host                                          \
            --volume=/:/rootfs:ro                               \
            --volume=/sys:/sys:ro                               \
            --volume=/dev:/dev                                  \
            --volume=/var/lib/docker/:/var/lib/docker:rw        \
            --volume=/var/lib/kubelet/:/var/lib/kubelet:rw      \
            --volume=/var/run:/var/run:rw                       \
            --pid=host                                          \
            --privileged=true                                   \
            gcr.io/google_containers/hyperkube:__KUBE_VERSION__ \
                /hyperkube kubelet                              \
                    --api-servers=http://localhost:8080         \
                    --v=2                                       \
                    --address=0.0.0.0                           \
                    --enable-server                             \
                    --hostname-override=127.0.0.1               \
                    --config=/etc/kubernetes/manifests-multi    \
                    --cluster-dns=__DNS_SERVER_IP__             \
                    --cluster-domain=__DNS_DOMAIN__
        """
        kubernetes_command = kubernetes_command_template \
            .replace("__KUBE_VERSION__", kube_version) \
            .replace("__DNS_SERVER_IP__", self._dns_server_ip) \
            .replace("__DNS_DOMAIN__", self._dns_domain)

        kube_proxy_command_template = """
        docker run -d                                           \
            --net=host                                          \
            --privileged                                        \
            gcr.io/google_containers/hyperkube:__KUBE_VERSION__ \
                /hyperkube proxy                                \
                    --master=http://127.0.0.1:8080              \
                    --v=2
        """
        kube_proxy_command = kube_proxy_command_template \
            .replace("__KUBE_VERSION__", kube_version)

        self.subprocess.call(etcd_command, shell=True)
        self.subprocess.call(kubernetes_command, shell=True)
        self.subprocess.call(kube_proxy_command, shell=True)

    def start_dns(self, args):
        import yaml
        import json

        with open("./commands/templates/local_cluster/dns-svc.yml") as stream:
            dns_svc_template_content = stream.read() \
                .replace("__DNS_SERVER_IP__", self._dns_server_ip)

        with open("./commands/templates/local_cluster/dns-rc.yml") as stream:
            dns_rc_template_content = stream.read() \
                .replace("__DNS_DOMAIN__", self._dns_domain) \
                .replace("__KUBE_SERVER_URL__", self._kube_server_url)

        for content in [dns_svc_template_content, dns_rc_template_content]:
            template = yaml.load(content)
            template["metadata"]["namespace"] = "kube-system"

            self._kubernetes.create_resource(
                    json.dumps(template),
                    self._kubernetes.resources_path,
                    "resource.yml"
            )

    def set(self, args):
        self.subprocess.call(
                self._kubernetes.kubectl + " config set-cluster dev --server=" +
                self._kube_server_url,
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

