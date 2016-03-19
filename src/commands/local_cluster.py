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

    def _start_etcd(self):
        etcd_command = """
            docker run \
                -d \
                --net=host \
                gcr.io/google_containers/etcd:2.2.1 \
                    /usr/local/bin/etcd \
                    --addr=127.0.0.1:4001  \
                    --bind-addr=0.0.0.0:4001 \
                    --data-dir=/var/etcd/data
        """
        self.subprocess.call(etcd_command, shell=True)

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

    def _start_proxy(self, kube_version, apiserver_port):
        proxy_template = """
            docker run \
            -d \
            --net=host \
            --pid=host \
            --privileged=true \
                tdeheurles/kubernetes:__KUBE_VERSION__ \
                    /hyperkube \
                        proxy \
                            --master=http://127.0.0.1:__APISERVER_PORT__ \
                            --v=2
        """
        proxy_command = proxy_template \
            .replace("__KUBE_VERSION__", kube_version) \
            .replace("__APISERVER_PORT__", apiserver_port)

        self.subprocess.call(proxy_command, shell=True)

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
        docker_host = args["docker_host"]
        apiserver_port = "8080"
        if "port" in args:
            apiserver_port = args["port"]

        self._start_dns(docker_host, apiserver_port)
        self._start_dashboard()

    def _start_dns(self, docker_host, apiserver_port):
        import yaml
        import json

        with open("./commands/templates/local_cluster/dns-svc.yml") as stream:
            dns_svc_template_content = stream.read()

        with open("./commands/templates/local_cluster/dns-rc.yml") as stream:
            dns_rc_template_content = stream.read() \
                .replace("__KUBE_SERVER_URL__", "http://" + docker_host + ":" + apiserver_port)

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

    def _start_kube2sky(self, apiserver_port):
        kube2sky_template = """
            docker run \
                -d \
                --net=host \
                gcr.io/google_containers/kube2sky:1.12 \
                    --kube_master_url=http://127.0.0.1:__APISERVER_PORT__ \
                    --domain=cluster.local \
        """
        kube2sky_command = kube2sky_template \
            .replace("__APISERVER_PORT__", apiserver_port)

        self.subprocess.call(kube2sky_command, shell=True)

    def _start_skydns(self):
        skydns_command = """
            docker run \
                -d \
                --net=host \
                gcr.io/google_containers/skydns:2015-10-13-8c72f8c \
                    --machines=http://localhost:4001 \
                    --addr=0.0.0.0:53 \
                    --domain=cluster.local \
                    --ns-rotate=false
        """
        self.subprocess.call(skydns_command, shell=True)

    # SAVE
    def _start_post12(self):
        pass
        # ==================
        # VERSION AFTER 1.2
        #   DO NOT DELETE
        # ==================
        # kubernetes_command_template = """
        # docker run -d \
        #     --volume=/:/rootfs:ro \
        #     --volume=/sys:/sys:ro \
        #     --volume=/var/lib/docker/:/var/lib/docker:rw \
        #     --volume=/var/lib/kubelet/:/var/lib/kubelet:rw \
        #     --volume=/var/run:/var/run:rw \
        #     --net=host \
        #     --pid=host \
        #     --privileged=true \
        #     tdeheurles/kubernetes:__K8S_VERSION__ \
        #         __PORT__
        # """
        # kubernetes_command = kubernetes_command_template \
        #     .replace("__K8S_VERSION__", kube_version) \
        #     .replace("__PORT__", "--port " + apiserver_port)
        # self.subprocess.call(kubernetes_command, shell=True)







