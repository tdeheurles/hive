# Hive

container to manage docker stuff

The project try to simplify the container process with docker, kubernetes and gcloud. Maybe I will add AWS and different kind of CLI with it too.

For now the project is a `prototype`, the api is really not fixed as I want it to match to a real utilisation.

### Documentation

Go [here](https://tdeheurles.gitbooks.io/hive/content/index.html) to see the documentation with a full [helloworld example](https://tdeheurles.gitbooks.io/hive/content/docs/helloworld/readme.html).

### Main points
- remove all dependencies other than docker
- regroup all common commands to
  - manage docker project (build/run/push)
  - manage kubernetes cluster (create a cluster/deploy on it)
- focus on developpers `have to` commands

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

- `local_cluster`: start a local kubernetes cluster
    - `create` generate a local cluster using kubernetes on docker
    - `start_addons` start kubernetes addons like DNS and Dashboard
    - `proxy` proxy a kubernetes service to the machine

##### Note
- the process is really similar to what we already do
- it does not solve complicated problems, but let the DEV focus on the mandatory part
- it should work on every platform as 99% run in container
- the code inside hive:
   - will be wrote once for all projects (or won't be written if you are just a user ^^
   - can be tested (harder to do with bash)
   - stay in the docker philosophy (I really think that it's not the case for CAPS)

### Issues
Do not hesitate to post an issue for any problem or question.