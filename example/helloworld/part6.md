# Deploying our application

In this part we will:
- generate the kubernetes manifest files with hive
- automate their configuration using hive variable system
- push our server docker image to docker.hub
- deploy our server into our cluster
- make some operations

### Generate the kubernetes manifests
We need to generate two files: 
- A replicationController manifest to manage our container in the cluster
- A service manifest to make our server accessible in the kubernetes environment

```bash
./hive template kubernetes myProjectName mySubProjectName --rc --svc
```

Look to your subproject, you will have a `kubernetes` folder with two yaml files:

- replicationController: `hive.rc.yml`

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: "<% mySubProjectName.name %>-<% mySubProjectName.major %>-<% mySubProjectName.minor %>-<% cli.id %>"
  labels:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
    minor: "<% mySubProjectName.minor %>"
    build: "<% cli.id %>"
spec:
  replicas: 1
  selector:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
    minor: "<% mySubProjectName.minor %>"
    build: "<% cli.id %>"
  template:
    metadata:
      labels:
        name: "<% mySubProjectName.name %>"
        major: "<% mySubProjectName.major %>"
        minor: "<% mySubProjectName.minor %>"
        build: "<% cli.id %>"
    spec:
      containers:
      - name: "<% mySubProjectName.name %>"
        image: "<% mySubProjectName.image %>:<% mySubProjectName.major %>.<% mySubProjectName.minor %>.<% cli.id %>"
        imagePullPolicy: Always
```

- service: `hive.svc.yml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: "<% mySubProjectName.name %>"
  labels:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
spec:
  selector:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
  ports:
  - port: 80
    targetPort: 80
    name: "http"
```

You can see that most of the elements are linked to our configuration file `hive.yml`.

The `port` is not linked to configuration element and is bind to 80. It's easy to update 80 to `<% mySubprojectName.port %>` and to do the same in the nginx configuration. That's where `hive variable` system start to remove pain of all this devops stuff.

Open the `hive.svc.yml` and add `spec.type: "LoadBalancer"` :
```yaml
apiVersion: v1
kind: Service
metadata:
  name: "<% mySubProjectName.name %>"
  labels:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
spec:
  selector:
    name: "<% mySubProjectName.name %>"
    major: "<% mySubProjectName.major %>"
  ports:
  - port: 80
    targetPort: 80
    name: "http"
  type: "LoadBalancer"
```
That new parameter will ask the google cluster to link mySubProjectName service to a PUBLIC IP.

### Push our container to docker.hub
Go to [docker hub](https://hub.docker.com/) and create an account.

Then loggin our docker client with your new credentials:

```bash
$ ./hive docker cli login
Username: tdeheurles
Password: xxxxxxxxx
Email: tdeheurles@gmail.com
WARNING: login credentials saved in /root/.docker/config.json
Login Succeeded
```
Your login are now saved in a data container named `hive_docker`.

Update your subproject image name to match your account in the `hive.yml` file. The image need to match `login/subprojectname`:
```
apiVersion: v0
kind: HiveConfig
spec:
  configuration:
    project: myProjectName
    maintainer: tdeheurles@gmail.com
    
    mySubProjectName:
      image: tdeheurles/mysubprojectname
      major: 0
      minor: 0
      base: nginx:1.9.7
      name: mysubprojectname
```

Build with the new image name:
```bash
$ ./hive do build myProjectName mySubProjectName id 0
Sending build context to Docker daemon 8.192 kB
Step 1 : FROM nginx:1.9.7
 ---> ef2443712c5b
Step 2 : MAINTAINER tdeheurles@gmail.com
 ---> Using cache
 ---> 5b1464e74220
Step 3 : COPY index.html /usr/share/nginx/html/index.html
 ---> Using cache
 ---> 35ec10fb5140
Successfully built 35ec10fb5140
```

And Push our project image:
```bash
$ ./hive do push myProjectName mySubProjectName id 0
The push refers to a repository [docker.io/tdeheurles/mysubprojectname]
b9d0b6d06bee: Pushed
5f70bf18a086: Pushed
0b3fbb980e2d: Pushed
40f240c1cbdb: Pushed
673cf6d9dedb: Pushed
ebfc3a74f160: Pushed
031458dc7254: Pushed
12e469267d21: Pushed
0.0: digest: sha256:14cc73daf69eafbe445df41278e7695c1a842da67a2a9df8c6012e0881e24fa8 size: 8127
The push refers to a repository [docker.io/tdeheurles/mysubprojectname]
b9d0b6d06bee: Layer already exists
5f70bf18a086: Layer already exists
0b3fbb980e2d: Layer already exists
40f240c1cbdb: Layer already exists
673cf6d9dedb: Layer already exists
ebfc3a74f160: Layer already exists
031458dc7254: Layer already exists
12e469267d21: Layer already exists
0.0.0: digest: sha256:02ff3a4f0370a12f3783302be2171ad2a09085a099b13e28bff6bd5f13cc3f4a size: 8129
```

### Let's deploy it
First control that our kubectl cli is linked to our cluster:
```bash
$ ./hive kubernetes cli get nodes
NAME                               LABELS                                                    STATUS    AGE
gke-mycluster-7dd21d65-node-c5g4   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-c5g4   Ready     28m
gke-mycluster-7dd21d65-node-lolq   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-lolq   Ready     39m
```

Then, deploy the id `0` of our application in the environment `test`:

```bash
$ ./hive kubernetes deploy myProjectName test 0
namespace "test" created

==================
service "mysubprojectname" created

==================
replicationcontroller "mysubprojectname-0-0-0" created
```

And control its status with:

```bash
$ ./hive kubernetes namespaces
NAME          LABELS                  STATUS    AGE
default       <none>                  Active    57m
kube-system   <none>                  Active    57m
test          project=myProjectName   Active    1m
```
Here we can see that our `test` environment is deployed. `default` and `kube-system` are environment used by the kubernetes cluster.
 
and:
```bash
$ ./hive kubernetes status test

==================== SERVICES ====================

NAME               CLUSTER_IP      EXTERNAL_IP   PORT(S)   SELECTOR                        AGE
mysubprojectname   10.19.255.185                 80/TCP    major=0,name=mysubprojectname   37s

======================= RC =======================

CONTROLLER               CONTAINER(S)       IMAGE(S)                            SELECTOR                                        REPLICAS   AGE
mysubprojectname-0-0-0   mysubprojectname   tdeheurles/mysubprojectname:0.0.0   build=0,major=0,minor=0,name=mysubprojectname   1          37s

====================== PODS ======================

NAME                           READY     STATUS    RESTARTS   AGE
mysubprojectname-0-0-0-bcf1p   1/1       Running   0          38s

====================== NODES =====================

NAME                               LABELS                                                    STATUS    AGE
gke-mycluster-7dd21d65-node-c5g4   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-c5g4   Ready     58m
gke-mycluster-7dd21d65-node-lolq   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-lolq   Ready     1h
```
Here we can see:
- our service `mysubprojectname` running on CLUSTER__IP 10.19.255.185 and exposing `port 80`
- the EXTERNAL_IP is blank as we need to wait around one minute for it to appear (re run the command in a minute)
- our replicationController `mysubprojectname-0-0-0`. It runs the image `tdeheurles/mysubprojectname:0.0.0` with `1 REPLICAS`
- the pod `mysubprojectname-0-0-0-bcf1p`. A pod is the kubernetes unit, it can host multiple container at once. Here it only host our container.

Run the command again to obtain your EXTERNAL__IP:
```bash
$ ./hive kubernetes status test

==================== SERVICES ====================

NAME               CLUSTER_IP      EXTERNAL_IP      PORT(S)   SELECTOR                        AGE
mysubprojectname   10.19.255.185   104.155.76.170   80/TCP    major=0,name=mysubprojectname   4m

======================= RC =======================

CONTROLLER               CONTAINER(S)       IMAGE(S)                            SELECTOR                                        REPLICAS   AGE
mysubprojectname-0-0-0   mysubprojectname   tdeheurles/mysubprojectname:0.0.0   build=0,major=0,minor=0,name=mysubprojectname   1          4m

====================== PODS ======================

NAME                           READY     STATUS    RESTARTS   AGE
mysubprojectname-0-0-0-bcf1p   1/1       Running   0          4m

====================== NODES =====================

NAME                               LABELS                                                    STATUS    AGE
gke-mycluster-7dd21d65-node-c5g4   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-c5g4   Ready     1h
gke-mycluster-7dd21d65-node-lolq   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-lolq   Ready     1h
```

And control that it work:
```bash
$ curl 104.155.76.170
Hello from the Hive
```

GREAT ^^ JOB DONE !

### SCALING
It's now really easy to scale up our application (as this application just require more pods). 
Just run the following command giving the environment `test`, the replication controller name `mysubprojectname-0-0-0` and the targeted number of replicas `5`:

```bash
$ ./hive kubernetes scale test mysubprojectname-0-0-0 5
replicationcontroller "mysubprojectname-0-0-0" scaled
```

Look at the updated status:
```bash
$ ./hive kubernetes status test

==================== SERVICES ====================

NAME               CLUSTER_IP      EXTERNAL_IP      PORT(S)   SELECTOR                        AGE
mysubprojectname   10.19.255.185   104.155.76.170   80/TCP    major=0,name=mysubprojectname   11m

======================= RC =======================

CONTROLLER               CONTAINER(S)       IMAGE(S)                            SELECTOR                                        REPLICAS   AGE
mysubprojectname-0-0-0   mysubprojectname   tdeheurles/mysubprojectname:0.0.0   build=0,major=0,minor=0,name=mysubprojectname   5          11m

====================== PODS ======================

NAME                           READY     STATUS    RESTARTS   AGE
mysubprojectname-0-0-0-2gu73   1/1       Running   0          1m
mysubprojectname-0-0-0-bcf1p   1/1       Running   0          11m
mysubprojectname-0-0-0-exfnj   1/1       Running   0          1m
mysubprojectname-0-0-0-j3rq6   1/1       Running   0          1m
mysubprojectname-0-0-0-lamgr   1/1       Running   0          1m

====================== NODES =====================

NAME                               LABELS                                                    STATUS    AGE
gke-mycluster-7dd21d65-node-c5g4   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-c5g4   Ready     1h
gke-mycluster-7dd21d65-node-lolq   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-lolq   Ready     1h
```
We have now 5 replicas of our application.

### Cleanup
We can stop the application (not the cluster) by running (don't do if you want to continue):
```bash
./hive kubernetes delete test
```

### Updating the application
Let's look at how to [update our application](part7.md)

### Billing
To stop the billing, you need to shutdown the cluster by running, do it if you don't want to continue the tutorial:
```bash
./hive gcloud delete mycluster
```
