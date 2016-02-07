# Hive

container to manage all our docker stuff

The project try to simplify the container process with docker, kubernetes and gcloud. Maybe I will add AWS and different kind of CLI with it too. 

### The problems I try to solve

To run container in automation, you need some glue to make everything work. Some use CAPS (chef, Ansible, Puppet, Salt), some use bash script ...

From my point of view, CAPS does not solve everything and you still need some bash at start or endpoint of your CAPS. On the other hand, bash can do lots of things but the code becomes quickly unreadable (for most people). 

An other issue is portability, a GNU bash comes with docker-toolbox on windows but it's a UNIX one on MAC. Lots of simple tools like rsync are not installed on these machines and  simple things can become complicated for nothing.

Kubernetes use manifests, these files are simple but you need to inject variables into it to make things automatic. Here too, you need some glue to do that.

### The keys to the solution

- Our project are made to run containers ... so why not define containers as our dependency, and only containers ^^.
- If I run my glue in a container, I can use another tool that don't need to be installed everywhere, this tool need to run quickly (quick start) as I want the container to be almost transparent, but the tool inside the container don't need to be portable anymore. Some languages seems to be good choice like python or maybe go. I have chosen python.

### My solution: `Hive`

Hive is just a simple CLI that propose tools for docker, gcloud, kubernetes and to simplify the glue. The gcloud and kubectl CLI are accessible from inside. But nothing is installed in this container. It just run other containers with the needed tools.
 
As an example, if you need to run a `kubectl cli` command. The normal way is to install it on linux or mac (you just can't on windows for now). With `hive`, you write this: `./hive kubernetes cli <your command>` when you would have run `./kubectl <your command>` with the CLI installed locally. I just need to add the `bash hive script` in my project and point to it when I need `gcloud or kubectl CLIs`. But the good points is that you can define gcloud or kubectl commands and and have a good feeling that the tool run without any need to install dependencies for the user.

Understand that `hive` will access your local docker, so it can start container, volume or clean things for you. The idea is not to confront with `docker-compose` or `kubelet`, I just want to list all the useful commands somewhere and to have an easy access to it for all my projects.

### What is done

hive services:
- `docker`:                run command with the docker client (for windows/mac, the commands are passed directly to the docker client of the VM, fixing some issues)
    - `cli`:                run docker commands
- `gcloud`:                Start a new container with gcloud installed
    - `init`:               setup the user account and project
    - `credentials`:        get the project credentials
    - `cli`:                run the gcloud CLI
- `kubernetes`:            see or manipulate kubernetes resources
    - `namespaces`:         list the namespaces of your kubernetes cluster
    - `create_environment`: generate a new environment (namespace)
    - `status`:             get the cluster resources for a given environment
    - `deploy`:             deploy a group of resources (using a declarative way)
    - `create`:             deploy a unique kubernetes resource
    - `scale`:              scale a service in a given namespace
    - `test_tool`:          start a test/debug service and connect to it
    - `delete`:             delete an environment
    - `cli`:                run kubectl commands
- `script`:                run your script under the hive container
    - `hive_run`:           run your code inside a container, using hive parameter system to simplify your glue
    - `run`:                run your code inside a container

### Example

##### You want to
run your application on kubernetes.

##### You write
- your Dockerfile
- (optional) a yaml configuration file to list your glue variables
- (optional) some bash to manage how the build will process (Dockerfile are too limitative in order to cache elements like package).
- your kubernetes manifests
- a deployment manifest

##### You run
The first time:
```bash
./hive gcloud init 
./hive gcloud credentials
```

Each time you want to build or deploy:
```bash
./hive script run <PATH_TO_BUILD_SCRIPT>
./hive kubernetes deploy <PATH_TO_DEPLOYMENT_MANIFEST>
```

##### Note
- the process is really similar to what we already do
- it should work on every platform
- the code inside hive:
   - will be wrote once for all projects (or won't be written if you are just a user ^^)
   - can be tested (harder to do with bash)
- go [here](docs/features) to see the main features

### TODO

- Documentation
- Tests. The program is in python, so I can write simple tests by mocking gcloud/docker etc.

