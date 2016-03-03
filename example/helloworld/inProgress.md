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

##### INIT THE CLUSTER (only once)
```bash
# get the account credentials
./hive gcloud init

# create a new cluster
./hive gcloud create_cluster myClusterName (#TODO)

# get your kubernetes credentials 
./hive gcloud credentials myClusterName
```
- All credentials (google account, kubernetes cluster) will be stored in data containers and can be used across all projects.
- A Google Container engine cluster is generated.


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
This will generate templates for you. As usual, it's template and it won't match every case, but you will just have to make few changes for most of the projects.

```bash
./hive kubernetes deploy myProjectName mySubprojectName id 0
```

