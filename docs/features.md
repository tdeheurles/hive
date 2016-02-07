# Features

- [installation](#installation)
- [docker](#docker)
- [gcloud](#gcloud)
- [script](#script)
  - [hive script run](#hive-script-run): run with the protection of your container
  - [hive script hive_run](#hive-script-hive_run): run inside a container with hive parameters system
- [kubernetes](#kubernetes)

### Installation
Copy this script in your project and name it `hive`:
```bash
#!/bin/bash

# Docker Toolbox test
dockerBinary="/usr/bin/docker"
if [[ ${DOCKER_MACHINE_NAME} == "default" ]];then
  dockerBinary="//usr/local/bin/docker"
fi

# Start hive
docker run -ti                                  \
  -v hive_docker:/root/.docker                  \
  -v hive_log:/hive_log                         \
  -v hive_share:/hive_share                     \
  -v //var/run/docker.sock:/var/run/docker.sock \
  -v ${dockerBinary}:/usr/bin/docker            \
  -v /$(pwd):/currentFolder                     \
  tdeheurles/hive:0.0 $@
```

The first part tries to identify docker toolbox and position your docker client (the one in the VM, not the Win/MAC one)

The second starts the container and shares some volumes:
- hive_docker:/root/.docker : to save your docker credentials
- hive_log : some log for hive debugging
- hive_share : to create persistency for recursive hive runs
- docker.sock and docker binary : to access the docker client
- current folder : to share the folder from where you run hive

---

### docker
The docker CLI is not one of the main features, but it solves some docker toolbox issues across versions.
At this moment it solves for me:
- loggin problems (error 403)

But I will use this to add the most common docker commands:
- clean the containers
- clean the volumes
- clean the `None` image
- etc

Test the docker access with:
```bash
$ ./hive docker cli ps
CONTAINER ID        IMAGE                 COMMAND                  CREATED                  STATUS                  PORTS               NAMES
bc3349ba3928        tdeheurles/hive:0.0   "python main.py docke"   Less than a second ago   Up Less than a second                       dreamy_easley
```

Will come some:
- `./hive docker clean`
- `./hive docker killAll`
- etc 

---

### gcloud
The hive gcloud commands simplify the google cloud process. Your users/devs won't need to install the gcloud CLI. Just run `./hive gcloud` and you can access gcloud CLI.

To prepare your cluster, you just need to run:
```bash
./hive gcloud init
./hive gcloud credentials
```
All the credentials will be saved in a volume.

---

### script
Hive script commands are still in design process. For now I have two different solutions :

#### ./hive script run
This one will just get a script and run it into your container. If it runs once, it will certainly be compatible with your users/devs. Note that it does not come with the hive variable system.

As an example, we can define a simple script that print `HelloWorld` :
```bash
#!/bin/bash

echo "HelloWorld from the Hive !"
```
We save it into our project under a `src` folder and name it `helloworld.sh`

The hive script (the one defined at the top of this page) needs to be in the same foder or a parent folder (hive won't see all your files as it will just share the current folder).

For our example, here is our folder structure (you will found it [here](../example/script_run)):

```
projectFolder
  ¦- hive
  ¦- src
      ¦- helloworld.sh
```

Then we can run it, from the [main folder of the project](../example/script_run):  
the signature is : `./hive script run PATH SCRIPT PARAMETERS`
```bash
./hive script run //src helloworld.sh
```
should print
```
HelloWorld from the Hive !
```

---

Now if we want to use some parameters, we can [update the script to something like this](../example/script_run_with_parameters):

```bash
#!/bin/bash

if [[ $# == 0 ]];then
  echo "usage:"
  echo "  $0 BUILD_NUMBER"
  exit 1
fi
echo "Our program will build with the number $build"
```

Then we can run again our hive script and try without and with a parameter:
```bash
$ ./hive script run //src build.sh
usage:
  ./build.sh BUILD_NUMBER
Command '['cd /currentFolder/src && ./build.sh ']' returned non-zero exit status 1

$ echo $?
1

$ ./hive script run //src build.sh 128
Our program will build with the number 128

$
```
You can see:
- our script have failed as the build number was not present.
- the error is propagated to the main script
- that finally, the script run normally 

---
But this example show also the variable mecanism of bash, I think it can be really complicated to just control some variable ... That's why I propose the hive_run script.

#### ./hive script hive_run
The hive_run script comes with a variable system. You can write variable into your scripts that will point directly to the CLI parameters or to a configuration file.

So first, lets [update the build parameter in our project](../example/scrip_hive_run):

```bash
#!/bin/bash

echo "Our program will build with the number <% args.build %>"
```
rename it `hive.build.sh` and invoke it with:
```bash
./hive script hive_run //src build.sh
```
will show
```bash
incorrect hive cli parameter for <% args.build %> in file hive.build.sh. No key value given
```
Our script invocation is automatically protected.

To make a good invoke, just provide the parameters in the command:
```bash
./hive script hive_run //src build.sh build 128
```
 will show:
 ```
 Our program will build with the number 128
 ```
 
 Note that:
 - `args` in `<% args.build %>` inform hive for a parameter of name `build` passed with the command line.
 - the file name is `hive.build.sh` and that we invoke it as `build.sh` in the command. If your script use other files with hive parameters, point to them without the `hive.` prefix.

 ---
 
 Now, let's run with parameters from a config file in the [next project](../example/script_hive_run_with_config). Rewrite the `hive.build.sh` like this:

```bash
 #!/bin/bash

echo "Our program will build with the number <% args.build %> and the parameter <% version.myproject.major %> from our config file"
```

and add a `config.yml` in our [project folder](../example/script_hive_run_with_config):

```yaml
apiVersion: v0
kind: HiveConfig
spec:
  version:
    myproject:
      minor: 1
```

run the script again:
```bash
$ ./hive script hive_run //src build.sh build 128
```
will print:
```
Please, rerun with the config parameter
```
So run again with the config file:
```bash
$ ./hive script hive_run --config config.yml //src build.sh build 128
```
will answer:
```
No configuration match for parameter <% version.myproject.major %> in file hive.build.sh
```
I did write minor instead of major in the configuration file ..., so after an update of the configuration file to:
```yaml
apiVersion: v0
kind: HiveConfig
spec:
  version:
    myproject:
      major: 1
```

```bash
$ ./hive script hive_run --config config.yml //src build.sh build 128
```
finally show:
```
Our program will build with the number 128 and the parameter 1 from our config file
```

You can see that you can easily define parameters and run them in your scripts. Hive will control them before invoking your script.

---

### kubernetes

The `hive kubernetes` commands comes with:
```
hive_command:
    create_environment  generate a new environment
    delete              delete an environment
    namespaces          some help
    deploy              deploy an application
    create              deploy a kubernetes resource
    status              get the cluster resources
    scale               scale a service in a given namespace
    test_tool           start a test/debug service and connect to in it
    cli                 run kubectl commands
```

Note that for this part, you need:
- a google account
- a google cloud project (need to give a credit card but it's free for first two months)
- to start a `google container engine` cluster
- to init your gcloud with:
  - `./hive gcloud init`
  - `./hive gcloud crdentials CLUSTER_NAME`

##### create_environment
```
usage: hive kubernetes create_environment [-h] [--project PROJECT]
                                          [--subproject SUBPROJECT]
                                          name

positional arguments:
  name                  the name of the environment

optional arguments:
  -h, --help            show this help message and exit
  --project PROJECT     A label to point to the project
  --subproject SUBPROJECT
                        A label to point to a sub-categorie
```
So we can create our environment with:
```bash
$ ./hive kubernetes create_environment hive-demo
```
```
namespace "hive-demo" created
```
We can also add labels to your environment (kubernetes namespace) by passing the `--project` and `--subproject` parameters:

```bash
$ ./hive kubernetes create_environment hive-demo --project main-project-name --subproject my-subproject
```

##### namespaces
We can look to our environment by running:
```bash
./hive kubernetes namespaces
```
```
NAME          LABELS                                               STATUS    AGE
default       <none>                                               Active    60d
hive-demo     project=main-project-name,subproject=my-subproject   Active    10s
kube-system   <none>                                               Active    60d
```

##### deploy
Hive comes with a simple solution to deploy a whole project made of multiple services.

We need to:
- create a yaml file to describe our project
- create a service/replicationController manifest template for each resource

We can:
- define all our parameters in a configuration file

Let's start with [an example project](../example/kubernetes_deploy).

The example will run a nginx server by using a replicationController and service.

First, let's create the `deployment.yml` manifest and put it in the project folder:
```yaml
apiVersion: v0
kind: HiveDeployment
spec:
  project:            simple-nginx
  deploymentStrategy: Recreate
  configuration:      config.yml
  templates:          templates

  services:
    - name: nginx-demo

  replicationController:
    - name: nginx-demo
```
This define:
- a name for project that will be used for labels.
- a strategy to delete and recreate or to automatically rolling update (rolling update need to be implemented)
- the `path` to the `config file` and to the `templates folder`
- the service name (that need to match a folder in the templates folder)
- the replication controller name (that need to match a folder in the templates folder)

Then we define our kubernetes manifests in `templates/nginx-demo/hive.rc.yml` and `templates/nginx-demo/hive.svc.yml`:
```yaml
# hive.svc.yml
apiVersion: v1
kind: Service
metadata:
  name: "nginx-demo"
  labels:
    name:  "nginx-demo"
    major: "<% version.simple-nginx.nginx-demo.major %>"
spec:
  selector:
    name:  "nginx-demo"
    major: "<% version.simple-nginx.nginx-demo.major %>"
  ports:
  - port: 80
    targetPort: 80
    name: "http"
```
```yaml
# hive.rc.yml
apiVersion: v1
kind: ReplicationController
metadata:
  name: "nginx-demo"
  labels:
    name: "nginx-demo"
    major: "<% version.simple-nginx.nginx-demo.major %>"
    minor: "<% version.simple-nginx.nginx-demo.minor %>"
    build: "<% args.build %>" 
spec:
  replicas: 1
  selector:
    name: "nginx-demo"
    major: "<% version.simple-nginx.nginx-demo.major %>"
    minor: "<% version.simple-nginx.nginx-demo.minor %>"
    build: "<% args.build %>"
  template:
    metadata:
      labels:
        name: "nginx-demo"
        major: "<% version.simple-nginx.nginx-demo.major %>"
        minor: "<% version.simple-nginx.nginx-demo.minor %>"
        build: "<% args.build %>"
    spec:
      containers:
      - name: "nginx-demo"
        image: "<% container.simple-nginx.nginx-demo %>:<% version.simple-nginx.nginx-demo.major %>.<% version.simple-nginx.nginx-demo.minor %>.<% args.build %>"
        imagePullPolicy: Always
        ports:
          - containerPort: 80
            name: "http"
```

We can write our configuration `config.yml`:
```yaml
apiVersion: v0
kind: HiveConfig
spec:
  container:
    simple-nginx:
      nginx-demo: "nginx"
  version:
    simple-nginx:
      nginx-demo:
        major: "1"
        minor: "9"
```

And finally we will just deploy our project. Look at the signature:

```bash
$ ./hive kubernetes deploy
error: too few arguments
usage: hive kubernetes deploy [-h] deployment_file environment build

positional arguments:
  deployment_file  the path to your deployment manifest
  environment      the name of the environment where you want to deploy your
                   application
  build            the build identifiant that you want to deploy

optional arguments:
  -h, --help       show this help message and exit
```

So, let's invoke the command:
```bash
./hive kubernetes deploy deployment.yml hive-demo 7
```
```
namespace "hive-demo" deleted
namespace "hive-demo" created
service "nginx-demo" created
replicationcontroller "nginx-demo" created
```
The `hive-demo` environment is deleted automatically as the startegy is set to `Recreate`, then we can see the namespace, service and replication controller created.

Look at the status of our environment:
```bash
$ ./hive kubernetes status hive-demo
```
```
SERVICES

NAME       CLUSTER_IP       EXTERNAL_IP   PORT(S)   SELECTOR                 AGE
nginx-demo 10.139.253.146   <none>        80/TCP    major=1,name=nginx-demo  2m

RC

CONTROLLER   CONTAINER(S)   IMAGE(S)      SELECTOR                                  REPLICAS   AGE
nginx-demo   nginx-demo     nginx:1.9.7   build=7,major=1,minor=9,name=nginx-demo   1          2m

PODS

NAME               READY     STATUS    RESTARTS   AGE
nginx-demo-e0rhe   1/1       Running   0          2m

ENDPOINTS

NAME       ENDPOINTS   AGE
nginx-demo <none>      2m

INGRESS

NAME      RULE      BACKEND   ADDRESS

NODES

NAME                             LABELS                                                  STATUS    AGE
gke-cluster-74a736d8-node-lmjw   kubernetes.io/hostname=gke-cluster-74a736d8-node-lmjw   Ready     23h
gke-cluster-74a736d8-node-zxeo   kubernetes.io/hostname=gke-cluster-74a736d8-node-zxeo   Ready     13d
```

Finally go to your cluster and open the external IP for your service:

```
Welcome to nginx!

If you see this page, the nginx web server is successfully installed and working. Further configuration is required.

For online documentation and support please refer to nginx.org.
Commercial support is available at nginx.com.

Thank you for using nginx.
```

##### create
TODO
##### status
TODO
##### scale
TODO
##### test_tool
TODO
##### delete
TODO
##### cli
TODO
