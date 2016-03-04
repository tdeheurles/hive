# Updating our application

In this part we will update the running application to a new one

### Make a change to the source

```bash
echo "Kevin Spacey is Kaiser Soze :p I know :p" > src/index.html
```

### Build the new container

```bash
$ ./hive do build myProjectName mySubProjectName id 1
Sending build context to Docker daemon 8.192 kB
Step 1 : FROM nginx:1.9.7
 ---> ef2443712c5b
Step 2 : MAINTAINER tdeheurles@gmail.com
 ---> Using cache
 ---> 5b1464e74220
Step 3 : COPY index.html /usr/share/nginx/html/index.html
 ---> Using cache
 ---> ac413f8faf48
Successfully built ac413f8faf48
```

### Push it

```bash
$ ./hive do push myProjectName mySubProjectName id 1
The push refers to a repository [docker.io/tdeheurles/mysubprojectname]
7473d962915e: Pushed
5f70bf18a086: Layer already exists
0b3fbb980e2d: Layer already exists
40f240c1cbdb: Layer already exists
673cf6d9dedb: Layer already exists
ebfc3a74f160: Layer already exists
031458dc7254: Layer already exists
12e469267d21: Layer already exists
0.0: digest: sha256:f81f5a690cdf931adfca5acfd3f97f7c33130ba4099ff4a4d25df14b7e68741f size: 8127
The push refers to a repository [docker.io/tdeheurles/mysubprojectname]
7473d962915e: Layer already exists
5f70bf18a086: Layer already exists
0b3fbb980e2d: Layer already exists
40f240c1cbdb: Layer already exists
673cf6d9dedb: Layer already exists
ebfc3a74f160: Layer already exists
031458dc7254: Layer already exists
12e469267d21: Layer already exists
0.0.0: digest: sha256:62310f01be1e32349d107c9fc6b783fab695941e8620ebe61765eeec149833ad size: 8129
```

### Deploy it
Wait a minute for the EXTERNAL_IP (Note that we get around this wait time by using nsgate)
```
$ ./hive kubernetes status test

==================== SERVICES ====================

NAME               CLUSTER_IP      EXTERNAL_IP      PORT(S)   SELECTOR                        AGE
mysubprojectname   10.19.255.187   104.155.93.152   80/TCP    major=0,name=mysubprojectname   1m

======================= RC =======================

CONTROLLER               CONTAINER(S)       IMAGE(S)                            SELECTOR                                        REPLICAS   AGE
mysubprojectname-0-0-1   mysubprojectname   tdeheurles/mysubprojectname:0.0.1   build=1,major=0,minor=0,name=mysubprojectname   1          1m

====================== PODS ======================

NAME                           READY     STATUS    RESTARTS   AGE
mysubprojectname-0-0-1-ih2as   1/1       Running   0          1m

====================== NODES =====================

NAME                               LABELS                                                    STATUS    AGE
gke-mycluster-7dd21d65-node-c5g4   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-c5g4   Ready     1h
gke-mycluster-7dd21d65-node-lolq   kubernetes.io/hostname=gke-mycluster-7dd21d65-node-lolq   Ready     1h
```

### Test it

```bash
$ curl 104.155.93.152
Kevin Spacey is Kaiser Soze :p I know :p
```

### Cleanup

```bash
./hive gcloud delete mycluster
```
