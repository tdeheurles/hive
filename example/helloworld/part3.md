# RUN IT

##### TRY IT
Now, let's run our `docker image` locally as a `docker container` (image are like class and container like instance):

```bash
$ ./hive do run myProjectName mySubProjectName id 0
key: <% mySubProjectName.name %> not found in configuration, please, rerun with the config parameter
```

The configuration stop you by asking another configuration parameter. It's the name of the container. A tag that is use to recognise it, to ask for the logs, kill it ... use something simple as it will be local, just know that it should be unique across your projects to not erase a container that is already running locally (not talking of kubernetes here).

Fill it in `hive.yml`:
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

And run the command again:
```bash
$ ./hive do run myProjectName mySubProjectName id 0
052120db382e7767b14a9ee42277bc36674a985560f4f135db01ca04ab530041
```
`052120db382e7767b14a9ee42277bc36674a985560f4f135db01ca04ab530041` is the id of your container. It can be used instead of the name we have defined before.

We can look to its logs by running:
```bash
$ docker logs mysubprojectname
hi
```

##### WHAT HAVE BEEN RUN
The script that `hive` have triggered is ``myProjectName/mySubprojectName/run/hive.run.sh`:
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
  ${image}.${id}
```

- As usual, we first get a list of parameter from configuration and cli
- then we ensure that a container with the name `mySubProjectName` is not running (with `docker kill`)
- finally run our container (`docker run`), as a daemon (`-d`) with the name `mySubProjectName`.

##### OK, BUT WHY DOES IT PRINT `hi` ?
This have been defined in our `build/hive.Dockerfile`:
```
FROM <% mySubProjectName.base %>
MAINTAINER <% maintainer %>

ENTRYPOINT ["echo", "hi"]
```
We have defined that: 
- our image is `ubuntu`: `FROM <% mySubProjectName.base %>`
- `echo hi` when we instantiate it: ENTRYPOINT ["echo", "hi"]

Note that a docker container stop after having done is job. So here, it just vanish after the console output.

We have run it as a daemon as hive is generally used to start services. It's what we look in the next chapter. 

##### SETUP OUR IMAGE AS A SERVICE
When you're done, let's setup a simple web server to host a Helloworld. Move to the [next chapter](part4.md)
