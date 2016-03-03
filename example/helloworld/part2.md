# Create our project

Create a folder for our project and move inside:
```bash
mkdir hive-helloworld
cd hive-helloworld
```

Note to mac/windows users: run all this steps by using the `Docker Quickstart Terminal` in order to have your terminal correctly setup with the docker environment parameters.

##### INSTALL HIVE IN YOUR PROJECT (only once per project)
Hive is just a bash script. You can install it by just copying it in your project. We propose `curl` to download it. You can also [download it by hand](https://github.com/tdeheurles/hive/releases/download/0.2.1/hive)

```bash
curl -L -O https://github.com/tdeheurles/hive/releases/download/0.2.1/hive
chmod 755 hive
```

##### GENERATE THE DEVOPS CODE (only once per project)
```bash
./hive template init myProjectName --maintainer tdeheurles@gmail.com
```
This will generate a folder `myProjectName` and a bootstrap for the project configuration in a `myProjectName/hive.yml` file.
 
```bash
./hive template docker myProjectName mySubProjectName --build --local
```
- This will generate a folder `mySubProjectName` in `myProjectName`. `--build` ask to generate the files to build and push your image while `--local` generates the files to run and kill your container.
- you should have the following structure:
```
hive-helloworld
 - myProjectName
   - mySubProjectName
     - build
       - hive.Dockerfile
       - hive.build.sh
       - hive.push.sh
     - run
       - hive.run.sh
     - kill
       - hive.kill.sh
   - hive.yml
 - hive
```
We will come back later to each of this elements.

##### BUILD
We will now build our `docker image`. 
The concerned elements are:
- `hive`: to run the commands
- `myProjectName/hive.yml`: to put the configuration
- `myProjectName/mySubprojectName/build/hive.Dockerfile` to automate the build of the docker image
- `myProjectName/mySubprojectName/build/hive.build.sh` to script the build and docker tags

Have a look to `myProjectName/mySubprojectName/build/hive.build.sh`:
```bash
#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% mySubProjectName.image %>:<% mySubProjectName.major %>.<% mySubProjectName.minor %>"

docker build -t ${image} .
docker tag ${image} ${image}.${id}
```
- The tag `<% cli.id %>` ask for a parameter from the CLI and the runtime
- The tags like `<% mySubProjectName.image %> are here to collect the configuration from the `myProjectName/hive.yml`
- Then we run a `docker build` and a `docker tag`
- note that this is a wanted simple template, build can be more complicated and we will look to that later

Lets try to build with:
```bash
$ ./hive do build myProjectName mySubProject
incorrect hive cli parameter for <% cli.id %> in file hive.build.sh. No key value given
```

`Hive` is complaining for a `cli parameter`, just give it by adding the key value` id 0` at our command:
```bash
$ ./hive do build myProjectName mySubProject id 0
key: <% mySubProjectName.image %> not found in configuration, please, rerun with the config parameter
```

Fine, the error have changed to a `configuration error`. We need to give hive our configuration.

As we sayed before, the configuration is done in the `myProjectName/hive.yml` file.

```yaml
apiVersion: v0
kind: HiveConfig
spec:
  configuration:
    project: myProjectName
    maintainer: tdeheurles@gmail.com
```

Open it in an editor and fill the configuration by running `./hive do build myProjectName mySubProject id 0` in order to ask hive all the needed configuration.
  
You should finish with something like this:
```yaml
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
      base: ubuntu:14.04.2
      name: mysubprojectname
```

Understand here that this will help to manage your project with an easy and protective configuration mecanism. We are not sure for now that having a pre-filled configuration is better as you will need to erase them for sure. A more direct way will be added soon where all the needed configuration will appear at once.

Finally, you should have something like that:
```
$ ./hive do build myProjectName mySubProjectName id 0
Sending build context to Docker daemon 7.168 kB
Step 1 : FROM ubuntu:14.04.2
 ---> 44ae5d2a191e
Step 2 : MAINTAINER tdeheurles@gmail.com
 ---> Using cache
 ---> 8cf229a0d8ca
Step 3 : ENTRYPOINT echo hi
 ---> Using cache
 ---> 4865a5f43307
Successfully built 4865a5f43307
```
Your docker image is built and you can see it by running `docker images`

```bash
$ docker images
REPOSITORY                      TAG                 IMAGE ID            CREATED             SIZE
tdeheurles/hive                 0.2                 0568b6f97fe4        20 hours ago        398.4 MB
tdeheurles/my-subproject-name   0.0                 4865a5f43307        33 hours ago        188.4 MB
tdeheurles/my-subproject-name   0.0.0               4865a5f43307        33 hours ago        188.4 MB
ubuntu                          14.04.2             44ae5d2a191e        6 months ago        188.4 MB
```
Where we can see :
- the base: `ubuntu:14.04.2`
- the hive builder: `tdeheurles/hive:0.2`
- our built image: `tdeheurles/my-subproject-name`

#### Run our project
When you're done, move to the [run our project page](part3.md).
