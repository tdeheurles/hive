class Kubernetes:
  def __init__(self, subprocess):
    self.subprocess = subprocess
    self.kube = [
        "docker", "run", "-ti",
        "-v", "gcloud_cache:/root/.config",
        "-v", "kube_cache:/root/.kube",
        "weareadaptive/gcloud:1.0", 
        "kubectl"
    ]
  def kubectl(self):
    self.subprocess.check_call(self.kube)
