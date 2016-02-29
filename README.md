# Hive

container to manage docker stuff

The project try to simplify the container process with docker, kubernetes and gcloud. Maybe I will add AWS and different kind of CLI with it too.

For now the project is a `prototype`, the api is really not fixed as I want it to match to a real utilisation.

### The problems I try to solve

To run container in automation, you need some glue to make everything work. Some use CAPS (chef, Ansible, Puppet, Salt), some use bash script ...

From my point of view, CAPS does not solve everything and you still need some bash at start or endpoint of your CAPS. On the other hand, bash can do lots of things but the code becomes quickly unreadable (for most people). 

An other issue is portability, a GNU bash comes with docker-toolbox on windows but it's a UNIX one on MAC. Lots of simple tools like rsync are not installed on these machines and  simple things can become complicated for nothing.

Kubernetes use manifests, these files are simple but as it's a description file, most of it change for each new deployment (versions, image, etc). Here too, you need some glue to do that.

Finally most of all these things have lots of common in different projects.

### The keys to the solution

- Our project are made to run containers ... so why not define containers as our only dependency.
- If I run my glue in a container, I can use another tool that don't need to be installed everywhere, this tool need to run quickly (quick start) as I want the container to be almost transparent, but the tool inside the container don't need to be portable anymore. Some languages seems to be good choice like python or maybe go. I have chosen python.

### My prototype: `Hive`

Hive is just a simple CLI that proposes tools for docker, gcloud, kubernetes 
and to simplify the glue. The gcloud and kubectl CLI are accessible from inside. 
This container comes with a docker client (it will use the host daemon), and python. 

It runs other containers with the needed tools:  
As an example, if you need to run a `kubectl cli` command. The normal way is to install it.   
With `hive`, you write this: `./hive kubernetes cli <your command>` when you would have run 
`./kubectl <your command>` with the CLI installed locally. 
A good points is that you can define gcloud or kubectl commands and have a good feeling that the tool run without any need to install dependencies for the user. It really remove lots of outdated readme problems.

Understand that `hive` will access your local docker, so it can start container, volume or clean things for you. The idea is not to confront with `docker-compose` or `kubelet`, I just want to list all the common useful commands somewhere and to have an easy access to it for all my projects.

### What is done

hive services:
```
- `docker`: run command with the docker client (for windows/mac, the commands are passed directly to the docker client of the VM, fixing some issues)
    - `cli` run docker commands

- `gcloud`: Start a new container with gcloud installed
    - `init`        setup the user account and project
    - `credentials` get the project credentials
    - `cli`         run the gcloud CLI

- `kubernetes`: see or manipulate kubernetes resources
    - `namespaces`         list the namespaces of your kubernetes cluster
    - `create_environment` generate a new environment (namespace)
    - `status`             get the cluster resources for a given environment
    - `deploy`             deploy a group of resources (using a declarative way)
    - `create`             deploy a unique kubernetes resource
    - `scale`              scale a service in a given namespace
    - `test_tool`          start a test/debug service and connect to it
    - `delete`             delete an environment
    - `cli`                run kubectl commands

- `do`: project managment tools
    - `build`  build a subproject or a project defined as a list of subproject. 
    - `run`    run a subproject/project.
    - `kill`   stop a subproject/project
    
- `template`: project generating tools
    - `init`        init a project in order to use the `do` commands with the hive parameter system
    - `docker`      init a subproject. This will let you build and run your project locally
    - `kubernetes`  generate the manifests needed by kubernetes.

```

### Example
`Note to Windows users:` This project generate lots of code that will run under linux environment and are sensitive to `LF` line endings. 
In order to ask your git to not update `LF` to `CRLF`, run `git config --global core.autocrlf false` before cloning the repositoty. Then run `git config --global core.autocrlf true` to have the previous behavior. 

#### You want to
create a dockerised application and be able to run it locally and on kubernetes.

#### You need to
##### INSTALL HIVE IN YOUR PROJECT (only once)
Move to the root of your project (sources need to be child folder/files of this root)
```bash
curl -O https://github.com/tdeheurles/hive/release/v0.2.1/hive
chmod 755 hive
```
The result is only a bash script added to your project

##### INIT THE CLUSTER (only once)
```bash
# get the account credentials
./hive gcloud init

# create a new cluster
./hive gcloud create_cluster myClusterName _(#TODO)

# get your kubernetes credentials 
./hive gcloud credentials myClusterName
```
- All credentials (google account, kubernetes cluster) will be stored in data containers and can be used across all projects.
- A Google Container engine cluster is generated.

##### GENERATE THE CODE (only once)
```bash
# create the project structure with the hive configuration file
./hive template init myProjectName --maintainer tdeheurles@gmail.com

# create a subproject and ask to generate the files to build, run, kill and push your containers
./hive template docker myProjectName mySubProjectName --build --local
```
- This will generate the folders and the needed files to develop locally

##### BUILD
```bash
./hive do build myProjectName mySubProject
```
At this point, hive will prompt you with something like: `key: <% mySubProjectName.image %> not found in configuration, please, rerun with the config parameters` to fill a list of configuration parameters.
`<% mySubprojectName.image %>` need to be field in `myProjectName/hive.yml`. Open it, you should have something like:
```yaml
apiVersion: v0
kind: HiveConfig
spec:
  configuration:
    project: myProjectName
    maintainer: tdeheurles@gmail.com
```
Fill it, following the hive `<% %>` requests.  
You should finish with something like this:
```yaml
apiVersion: v0
kind: HiveConfig
spec:
  configuration:
    project: myProjectName
    maintainer: tdeheurles@gmail.com
    mySubProjectName:
      image: tdeheurles/my-subproject-name
      major: 0
      minor: 0
      base: ubuntu:14.04.2
```
Understand here that this will help to manage your project with an easy and protective configuration mecanism.
Hive will now complain of `incorrect hive cli parameter for <% args.id %> in file hive.build.sh. No key value given`

The difference with the previous one is that this kind of parameter are `runtime parameters`. You need to fill it when you invoke `hive`:
```bash
# just give the name of the parameter (id) as a key and follow with the value (0)
./hive do build myProjectName mySubProject id 0
```
You now have a docker image that you can see by running `docker images`
```bash
$ docker images
REPOSITORY                      TAG                 IMAGE ID            CREATED             SIZE
tdeheurles/hive                 0.2                 0568b6f97fe4        20 hours ago        398.4 MB
tdeheurles/my-subproject-name   0.0                 4865a5f43307        33 hours ago        188.4 MB
tdeheurles/my-subproject-name   0.0.0               4865a5f43307        33 hours ago        188.4 MB
ubuntu                          14.04.2             44ae5d2a191e        6 months ago        188.4 MB
```
Here we can see :
- the base: `ubuntu:14.04.2`
- the hive builder: `tdeheurles/hive:0.2`
- our built image: `tdeheurles/my-subproject-name`

##### RUN IT
```bash
./hive do run myProjectName mySubProjectName id 0
```
and look at the logs:
```bash
$ docker logs my-subproject-name
hi
```

##### PUSH IT
```bash
./hive do push myProjectName mySubProjectName id 0
The push refers to a repository [docker.io/tdeheurles/my-subproject-name]
5f70bf18a086: Pushed
1255f0fad851: Pushed
3bd5a069ac09: Pushed
fef0f9958347: Pushed
0.0: digest: sha256:3be0ddf74b163bfbd6aef02e570e95f524f7817c2f5c150366b584649a075a31 size: 5265
The push refers to a repository [docker.io/tdeheurles/my-subproject-name]
5f70bf18a086: Layer already exists
1255f0fad851: Layer already exists
3bd5a069ac09: Layer already exists
fef0f9958347: Layer already exists
0.0.0: digest: sha256:155b02f2e786524dffa01795ff5fd1bf45d22301c514f45bfd514dc54851d23a size: 5267
```

##### DEPLOY IT
First generate the kubernetes manifests
```bash
./hive template kubernetes myProjectName mySubprojectName --rc --svc
```
This commands ask to generate the kubernetes manifests for your project. You can find them in the folder `myProjectName/mySubprojectName/kubernetes`:
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
This will generate templates for you. As usual, it's template, it won't match everycase, but you will just have to make few changes.

```bash
./hive kubernetes deploy myProjectName mySubprojectName id 0
```

##### Note
- the process is really similar to what we already do
- it should work on every platform
- the code inside hive:
   - will be wrote once for all projects (or won't be written if you are just a user ^^)
   - let the DEV focus on the mandatory part
   - can be tested (harder to do with bash)
   - stay in the docker philosophy (I really think that it's not the case for CAPS)

### TODO

- update [features in documentation](docs/features.md)
- Tests (mock the os/kubernetes/gcloud).

