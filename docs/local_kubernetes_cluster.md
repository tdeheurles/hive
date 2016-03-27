# Local kubernetes cluster

You can easily generate a local kubernetes cluster with hive. The solution used is kubernete on docker.

For now, there are two steps to generate it:
- Start the cluster
- Start the addons (dashboard/DNS)

The docker virtual machine needs some mount updates before running the kubernetes containers. You can do that by running hive with the option `-i`.

Also, a proxy command ease how to connect to your services. 

### The local_cluster commands
```console
$ ./hive local_cluster
error: too few arguments
usage: hive local_cluster [-h] {create,proxy,start_addons} ...

optional arguments:
  -h, --help            show this help message and exit

hive_command:
  {create,proxy,start_addons}
    create              start a local kubernetes cluster
    proxy               start a proxy for your local kubernetes cluster
    start_addons        start the addons for your cluster (DNS, Dashboard,
                        ...)
```

### Start the local cluster
Here is the local_cluster `create` help
```console
$ ./hive local_cluster create -h
usage: hive local_cluster create [-h] [--version VERSION] [--port PORT]
                                 docker_host

positional arguments:
  docker_host        The docker host, for docker-toolbox use something like
                     192.168.99.100, for linux use localhost

optional arguments:
  -h, --help         show this help message and exit
  --version VERSION  kubernetes version in the form v1.1.8
  --port PORT        the port you want for the apiserver. default is 8080
  ```
  
The options are the version of the kubernetes cluster and the port for the apiserver. Only the version after v1.2.0 are supported.

Note that the first time you create your cluster, the `-i` option need to be added to hive.

##### example
On windows with docker-toolbox:
```console
$ ./hive -i local_cluster create 192.168.99.100 --port 9000
the default machine is now ready for a local-kubernetes-cluster
5520870726d09024becb5440b461314fd9cf1b83858da44a5ae1f629764fe111
Setting local kubernetes as kubectl context
cluster "dev" set.
context "dev" set.
switched to context "dev".

$ docker ps
CONTAINER ID        IMAGE                                 COMMAND                  CREATED             STATUS              PORTS               NAMES
ad5df415e283        tdeheurles/kubernetes:v1.2.0          "/hyperkube apiserver"   9 seconds ago       Up 16 seconds                           k8s_apiserver.aaedc193_k8s-master-default_default_33434a15201de304c645f9059e2496d7_0919c81d
7061ed0a3539        tdeheurles/kubernetes:v1.2.0          "/hyperkube controlle"   10 seconds ago      Up 17 seconds                           k8s_controller-manager.834844ae_k8s-master-default_default_33434a15201de304c645f9059e2496d7_21d86c63
a370fb456fd9        tdeheurles/kubernetes:v1.2.0          "/setup-files.sh IP:1"   10 seconds ago      Up 17 seconds                           k8s_setup.f87e2b66_k8s-master-default_default_33434a15201de304c645f9059e2496d7_beee3599
15a8027ec64d        tdeheurles/kubernetes:v1.2.0          "/hyperkube scheduler"   10 seconds ago      Up 17 seconds                           k8s_scheduler.a5c8f607_k8s-master-default_default_33434a15201de304c645f9059e2496d7_ab2d1cd0
cab199e805e7        gcr.io/google_containers/etcd:2.2.1   "/usr/local/bin/etcd "   10 seconds ago      Up 17 seconds                           k8s_etcd.7e452b0b_k8s-etcd-default_default_1df6a8b4d6e129d5ed8840e370203c11_2c503445
da932cf0b964        tdeheurles/kubernetes:v1.2.0          "/hyperkube proxy --m"   10 seconds ago      Up 17 seconds                           k8s_kube-proxy.ae0f419c_k8s-proxy-default_default_0ebff37f3737903b25f94ad16a3e5db0_e849ca25
b54e666459fd        gcr.io/google_containers/pause:2.0    "/pause"                 10 seconds ago      Up 17 seconds                           k8s_POD.6059dfa2_k8s-master-default_default_33434a15201de304c645f9059e2496d7_a3b5a719
059046ad2a9e        gcr.io/google_containers/pause:2.0    "/pause"                 10 seconds ago      Up 17 seconds                           k8s_POD.6059dfa2_k8s-etcd-default_default_1df6a8b4d6e129d5ed8840e370203c11_66266f1e
220789c11e61        gcr.io/google_containers/pause:2.0    "/pause"                 10 seconds ago      Up 17 seconds                           k8s_POD.6059dfa2_k8s-proxy-default_default_0ebff37f3737903b25f94ad16a3e5db0_07e0acda
5520870726d0        tdeheurles/kubernetes:v1.2.0          "/start.sh --port 900"   16 seconds ago      Up 23 seconds                           pedantic_tesla
```

And you can control your apiserver service:
```json
{
    paths: [
        "/api",
        "/api/v1",
        "/apis",
        "/apis/autoscaling",
        "/apis/autoscaling/v1",
        "/apis/batch",
        "/apis/batch/v1",
        "/apis/extensions",
        "/apis/extensions/v1beta1",
        "/healthz",
        "/healthz/ping",
        "/logs/",
        "/metrics",
        "/resetMetrics",
        "/swagger-ui/",
        "/swaggerapi/",
        "/ui/",
        "/version"
    ]
}
```

### Start the addons
Here is the local_cluster `start_addons` help
```console
$ ./hive local_cluster start_addons -h
usage: hive local_cluster start_addons [-h] [--port PORT]

optional arguments:
  -h, --help   show this help message and exit
  --port PORT  the port of the apiserver. default is 8080
```

##### Example
```console
$ ./hive local_cluster start_addons --port 9000
service "kube-dns" created
replicationcontroller "kube-dns-v11" created
service "k8s-dashboard" created
replicationcontroller "k8s-dashboard" created

$ docker ps
CONTAINER ID        IMAGE                                                        COMMAND                  CREATED                  STATUS              PORTS               NAMES
79ad28fd0fe0        gcr.io/google_containers/kubernetes-dashboard-amd64:v1.0.0   "/dashboard --port=90"   Less than a second ago   Up 7 seconds                            k8s_k8s-dashboard.e1b68fc9_k8s-dashboard-hoaff_default_955bab0e-f447-11e5-914a-7e995b3eadaf_669add49
de006173a3a1        gcr.io/google_containers/etcd-amd64:2.2.1                    "/usr/local/bin/etcd "   1 seconds ago            Up 8 seconds                            k8s_etcd.b2de3551_kube-dns-v11-cxsts_default_94c1b384-f447-11e5-914a-7e995b3eadaf_02c59a8e
9a22efb3baa5        gcr.io/google_containers/exechealthz:1.0                     "/exechealthz '-cmd=n"   4 seconds ago            Up 8 seconds                            k8s_healthz.7174149f_kube-dns-v11-cxsts_default_94c1b384-f447-11e5-914a-7e995b3eadaf_f365f541
5aa5c9f52bf3        gcr.io/google_containers/skydns:2015-10-13-8c72f8c           "/skydns -machines=ht"   4 seconds ago            Up 11 seconds                           k8s_skydns.ac0d3af2_kube-dns-v11-cxsts_default_94c1b384-f447-11e5-914a-7e995b3eadaf_2f248ee3
1368bb08d767        gcr.io/google_containers/pause:2.0                           "/pause"                 4 seconds ago            Up 11 seconds                           k8s_POD.3a1c00d7_k8s-dashboard-hoaff_default_955bab0e-f447-11e5-914a-7e995b3eadaf_ea421283
588c23aba9f7        gcr.io/google_containers/kube2sky:1.14                       "/kube2sky --domain=c"   5 seconds ago            Up 11 seconds                           k8s_kube2sky.2432018b_kube-dns-v11-cxsts_default_94c1b384-f447-11e5-914a-7e995b3eadaf_6def0614
c5e88ff299dc        gcr.io/google_containers/pause:2.0                           "/pause"                 5 seconds ago            Up 12 seconds                           k8s_POD.e2764897_kube-dns-v11-cxsts_default_94c1b384-f447-11e5-914a-7e995b3eadaf_4ef90422
ad5df415e283        tdeheurles/kubernetes:v1.2.0                                 "/hyperkube apiserver"   About a minute ago       Up About a minute                       k8s_apiserver.aaedc193_k8s-master-default_default_33434a15201de304c645f9059e2496d7_0919c81d
7061ed0a3539        tdeheurles/kubernetes:v1.2.0                                 "/hyperkube controlle"   About a minute ago       Up About a minute                       k8s_controller-manager.834844ae_k8s-master-default_default_33434a15201de304c645f9059e2496d7_21d86c63
a370fb456fd9        tdeheurles/kubernetes:v1.2.0                                 "/setup-files.sh IP:1"   About a minute ago       Up About a minute                       k8s_setup.f87e2b66_k8s-master-default_default_33434a15201de304c645f9059e2496d7_beee3599
15a8027ec64d        tdeheurles/kubernetes:v1.2.0                                 "/hyperkube scheduler"   About a minute ago       Up About a minute                       k8s_scheduler.a5c8f607_k8s-master-default_default_33434a15201de304c645f9059e2496d7_ab2d1cd0
cab199e805e7        gcr.io/google_containers/etcd:2.2.1                          "/usr/local/bin/etcd "   About a minute ago       Up About a minute                       k8s_etcd.7e452b0b_k8s-etcd-default_default_1df6a8b4d6e129d5ed8840e370203c11_2c503445
da932cf0b964        tdeheurles/kubernetes:v1.2.0                                 "/hyperkube proxy --m"   About a minute ago       Up About a minute                       k8s_kube-proxy.ae0f419c_k8s-proxy-default_default_0ebff37f3737903b25f94ad16a3e5db0_e849ca25
b54e666459fd        gcr.io/google_containers/pause:2.0                           "/pause"                 About a minute ago       Up About a minute                       k8s_POD.6059dfa2_k8s-master-default_default_33434a15201de304c645f9059e2496d7_a3b5a719
059046ad2a9e        gcr.io/google_containers/pause:2.0                           "/pause"                 About a minute ago       Up About a minute                       k8s_POD.6059dfa2_k8s-etcd-default_default_1df6a8b4d6e129d5ed8840e370203c11_66266f1e
220789c11e61        gcr.io/google_containers/pause:2.0                           "/pause"                 About a minute ago       Up About a minute                       k8s_POD.6059dfa2_k8s-proxy-default_default_0ebff37f3737903b25f94ad16a3e5db0_07e0acda
5520870726d0        tdeheurles/kubernetes:v1.2.0                                 "/start.sh --port 900"   About a minute ago       Up About a minute                       pedantic_tesla
``` 
