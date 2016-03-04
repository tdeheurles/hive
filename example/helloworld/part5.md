# Create a kubernetes cluster on gcloud

Hive can manage simple parts of a gcloud kubernetes cluster.  
Note that hive can connect to any kubernetes cluster (not only gcloud ones).

### Credentials

In order to have access to gcloud, you need to create a project or be added to an existing project. 
A gcloud project can host multiple cluster. 
If the project is already created, ask your admin/devops guy to add you to the project. 
Else you can create one and benefit from 2 month free.

If you don't have a project:
go to [this page](https://cloud.google.com/container-engine/docs/before-you-begin#sign_up_for_a_google_account) and follow tutorial until the `install gcloud part` excluded.  

You should have done:
- sign up for google account
- enable billing
- enable the container engine app (after creating a project).

Now we can get your gcloud credentials:
```bash
$ ./hive gcloud init
hive_cache_gcloud
Welcome! This command will take you through the configuration of gcloud.

Your current configuration has been set to: [default]

To continue, you must login. Would you like to login (Y/n)?  y
```
Just say `y` then:
```
Go to the following link in your browser:

    https://accounts.google.com/o/oauth2/auth?redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&prompt=select_account&response_type=code&client_id=325
594559.apps.googleusercontent.com&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-plat
form+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute&access_type=offline


Enter verification code: 4/5eFpMqiO8ZhZ6GQr7VPTx_B0lkcWWR5yKrZGkDc
```
Copy/Paste the link to a browser (work with firefox/ie - some issue with chrome), make your authentication and copy the token back to your CLI:
```
You are now logged in as: [tdeheurles@gmail.com]

Pick cloud project to use:
 [1] [myProjectName]
 [2] [myOtherProjectName]
Please enter your numeric choice:  1
```
Choose your project by using the int id
```
Your current project has been set to: [myProjectName].

Your project default compute zone has been set to [europe-west1-c].
You can change it by running [gcloud config set compute/zone NAME].

Your project default compute region has been set to [europe-west1].
You can change it by running [gcloud config set compute/region NAME].

Do you want to use Google's source hosting (see
https://cloud.google.com/tools/cloud-repositories/) (Y/n)?  n
```
As our project have already a git, answrer `n`
```
gcloud has now been configured!
You can use [gcloud config] to change more gcloud settings.

Your active configuration is: [default]

[compute]
region = europe-west1
zone = europe-west1-c
[core]
account = tdeheurles@gmail.com
disable_usage_reporting = False
project = myProjectName
```

Our credentials are now saved into a data container named `hive_cache_gcloud`. You won't need to do that for each project.

### create a cluster
To create a cluster, we need to choose the datacenter and the kind of node. 

Show the possibilities:
```bash
$ ./hive gcloud show
NAME           ZONE           CPUS MEMORY_GB DEPRECATED
[ ... ]

f1-micro       asia-east1-c   1     0.60
g1-small       asia-east1-c   1     1.70
n1-highcpu-16  asia-east1-c   16   14.40
f1-micro       europe-west1-d 1     0.60
g1-small       europe-west1-d 1     1.70
n1-highcpu-16  europe-west1-d 16   14.40
n1-highcpu-2   europe-west1-d 2     1.80
n1-highcpu-32  europe-west1-d 32   28.80
n1-highcpu-4   europe-west1-d 4     3.60
n1-highcpu-8   europe-west1-d 8     7.20
n1-highmem-16  europe-west1-d 16   104.00
n1-highmem-2   europe-west1-d 2    13.00
n1-highmem-32  europe-west1-d 32   208.00
n1-highmem-4   europe-west1-d 4    26.00
n1-highmem-8   europe-west1-d 8    52.00
n1-standard-1  europe-west1-d 1     3.75
n1-standard-16 europe-west1-d 16   60.00
n1-standard-2  europe-west1-d 2     7.50
n1-standard-32 europe-west1-d 32   120.00
n1-standard-4  europe-west1-d 4    15.00
n1-standard-8  europe-west1-d 8    30.00

[ ... ]
```
Here is a part of the long list of what you can choose. We will setup a cluster named `mycluster` in `europe-west1-b` with nodes of kind `n1-standard-1`:
```bash
$ ./hive gcloud create_cluster mycluster europe-west1-b n1-standard-1
create command can take a few seconds ...
Creating cluster mycluster...done.
 Created [https://container.googleapis.com/v1/projects/myprojectname/zones/europe-west1-b/clusters/mycluster].
kubeconfig entry generated for mycluster.
NAME       ZONE            MASTER_VERSION  MASTER_IP        MACHINE_TYPE   NODE_VERSION  NUM_NODES  STATUS
mycluster  europe-west1-b  1.1.8           104.156.108.20   n1-standard-1  1.1.8         1          RUNNING
```
 
Just wait a few minutes for the setup to proceed and you will have kubernetes cluster. Don't forget that billing is started from this moment (around 1$ per day or 0.007$ per minutes). Deleting the cluster stop the billing.
 
### set autoscaling on for our cluster (optional)
We now ask the gcloud cluster to scale automatically if we add too much containers. We ask the nodes to target 75% of CPU on each nodes. Kubernetes will move your container to reorganise the number of nodes.
 
We autoscale the cluster named `mycluster` with a target of `0.75` of CPU, a maximum of `5` nodes and we tell the monitoring to wait `120` seconds after a node count change before taking a new decision:
```bash
$ ./hive gcloud autoscale mycluster 0.75 5 120
autoscale command can take a few seconds ...
Created [https://www.googleapis.com/compute/v1/projects/myprojectname/zones/europe-west1-b/autoscalers/gke-mycluster-7dd21d65-group-i9ps].
---
autoscalingPolicy:
  coolDownPeriodSec: 120
  cpuUtilization:
    utilizationTarget: 0.75
  maxNumReplicas: 5
  minNumReplicas: 2
creationTimestamp: '2016-03-04T07:24:57.188-08:00'
id: '5869340100973041190'
kind: compute#autoscaler
name: gke-mycluster-7dd21d65-group-i9ps
selfLink: https://www.googleapis.com/compute/v1/projects/myprojectname/zones/europe-west1-b/autoscalers/gke-mycluster-7dd21d65-group-i9ps
target: gke-mycluster-7dd21d65-group
zone: europe-west1-b
```

### stop the google billing
For your information, it's easy to cleanup our cluster (but don't do it if you want to continue the tutorial).

```bash
./hive gcloud delete mycluster
```
And that's all

### deploy our application
Now that our cluster is up, we can [deploy our application](part6.md).
