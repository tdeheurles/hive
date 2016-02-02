# Hive

container to manage all our docker stuff

The project try to simplify the container process with docker, kubernetes and gcloud. Maybe I will add AWS and different kind of CLI with it too. 

### The problem I try to solve

To run container in automation, you need some glue to make everything work. Some use CAPS (chef, Ansible, Puppet, Salt), some use bash script ...

From my point of view, CAPS does not solve everything and you still need some bash at start or endpoint of your CAPS. On the otherhand, bash can do lots of things but the code becomes quickly unreadable for most of people). An other issue is portability, a GNU bash comes with docker-tooolbox on windows but it's a UNIX one on MAC. Lots of simple tools like rsync are not installed on these machines and lots of simple things can become complicated for nothing.

### The solution I propose

- The idea is to run container ... so we know we can use containers as a dependency without any cost than the download of this one.
- If I run my script in a container, I can use another tool that don't need to be installed everywhere.
- The tool need to run quickly (quick start) as I want the container to be almost transparent.

So I propose here a container that run a python program to manage our container stuff. 

It's just a simple CLI that propose tools for docker, gcloud and kubernetes. The gcloud and kubectl CLI are accessible from inside. But nothing is installed in the this container. It just run another container with the needed tool.
 
As an example, if you need to run a `kubectl cli` command. The normal way is to install it on linux or mac (you just can't on windows). Here you write this: `./hive kubernetes cli <your command>` where you would have run `./kubectl <your command>` if you were local. The good point is I just need to add the `bash hive script` in my project and point to it when I need `gcloud or kubectl CLIs`. 

An other point is that the tool can manage your local docker. So it can start container, volume or clean things for you. The idea here is not to confront with `docker-compose` or `kubectl`, I just want to list all the usefull commands somewhere and to have easy access to it.

### What is done

- some docker commands for demo
- gcloud cli (with cache for user in a volume)
- kubectl cli (with cache for configuration in a volume)

### Example

##### You want to
run your application on kubernetes.

##### You write
- your Dockerfile
- some bash to manage how the build will process (Dockerfile are too limitative in order to cache elements like package) 
- your kubernetes manifests

##### You run
```bash
./hive docker build <PATH_TO_BUILD_SCRIPT>
./hive gcloud init 
# You follow the process to login
./hive gcloud credentials
./hive kubectl create -f <PATH_TO_MANIFEST_FOLDER>
```

##### Note
- the process is really similar to what we already do
- it should work on every platform
- the code inside hive:
   - will be wrote once for all projects
   - can be tested (hard to do with bash)

### TODO

- Documentation
- Tests. The program is in python, so I can write simple tests by mocking gcloud/docker etc.
- Build mecanism and design.
- Deploy mecanism and design.
