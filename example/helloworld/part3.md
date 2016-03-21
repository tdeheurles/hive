# SETUP OUR IMAGE AS A SERVICE

So, let's generate a really simple helloworld project.  
We will build a nginx container that will host a index.html page.

### Generate the sources
```
mkdir src
echo "Hello from the Hive" > src/index.html
```

and that's all as it's a really simple project.

### Generate the nginx configuration

We will now setup a more ambitious container build.  
We need to:
- set nginx as the base image (see the [docker.hub for nginx](https://hub.docker.com/_/nginx/))
- update our container build to copy the index.html and start nginx when we run it

##### set nginx as the base image
Just open `devops/hive.yml` and change the base image to `nginx:1.9.7`
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
      base: nginx:1.9.7
      name: mysubprojectname
```

##### update our container build and run mecanism to match nginx requirement
Open the `hive.Dockerfile` in an editor and make it like that:
```
FROM <% mySubProjectName.base %>
MAINTAINER <% maintainer %>

COPY index.html /usr/share/nginx/html/index.html
```
- we remove the entrypoint (the container will use the one from the nginx image
- we add `COPY index.html /usr/share/html/index.html

As docker build can only copy the files that are in its context, we need to add index.html to its context by copying it to the Dockerfile folder.

Open `hive.build.sh` and update it like that:
```bash
#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% mySubProjectName.image %>:<% mySubProjectName.major %>.<% mySubProjectName.minor %>"

# get the sources
cp ../../../src/index.html .

# build and tag
docker build -t ${image} .
docker tag ${image} ${image}.${id}

# cleanup the directory
rm index.html
```
Note that this part is not automated as we think that each project will be special. Just do what you need. The good part is that you know that this code will be run inside a linux container and will be portable across environment.

Finally, open `hive.run.sh` and make it match our new intention: `serve port 80`:
```bash
#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% mySubProjectName.image %>:<% mySubProjectName.major %>.<% mySubProjectName.minor %>"
container="<% mySubProjectName.name %>"

docker kill ${container} 2&> /dev/null || true
docker rm   ${container} 2&> /dev/null || true
docker run -d         \
  --name ${container} \
  -p 80:80            \
  ${image}.${id}
```
We have just added a `-p 80:80` line to the `docker run`

### build and run it
And now, build run test and kill ...
```console
# BUILD
$ ./hive do build myProjectName mySubProjectName id 1

# RUN
$ ./hive do run   myProjectName mySubProjectName id 1

# TEST
$ curl 192.168.99.100
Hello from the Hive

# KILL
$ ./hive do kill myProjectName mySubProjectName
mysubprojectname
```
Note that I'm using `192.168.99.100` as I'm running it from a Windows Host with docker-toolbox.

### let's deploy it to a kubernetes cluster
But first we need a kubernetes cluster ... ^^  
So let's [generate one](part4.md)
