from Docker import getDockerVolumes

class Gcloud:
  def __init__(self, subprocess):
    self.subprocess = subprocess
    self.gcloud = [
        "docker", "run", "-ti",
        "-v", "gcloud_cache:/root/.config",
        "-v", "kube_cache:/root/.kube",
        "weareadaptive/gcloud:1.0", 
        "gcloud"
    ]

  def init(self):
    volumes = getDockerVolumes()
    if not "gcloud_cache" in [volume.name for volume in volumes]:
      self.subprocess.check_call(["docker", "volume", "create", "--name=gcloud_cache"])
      self.subprocess.check_call(["docker", "volume", "create", "--name=kube_cache"])
      self.subprocess.check_call(self.gcloud + ["init"])
    else:
      print "already logged"

  def getCredentials(self, cluster):
    self.subprocess.check_call(self.gcloud + ["container", "clusters", "get-credentials", cluster])