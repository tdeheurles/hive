import argparse
import subprocess

from modele.Gcloud import Gcloud
from modele.Volume import Volume
from modele.Kubernetes import Kubernetes
from modele.Docker import getDockerVolumes

commands = {
    "bash":       { "type":"call", "cmd": ["docker", "run", "-ti", "tdeheurles/hive:0.0", "bash"]},
    "dps":        { "type":"call", "cmd": ["docker", "ps"] },
    "dim":        { "type":"call", "cmd": ["docker", "images"] },
    "dvl":        { "type":"call", "cmd": ["docker", "volume", "ls"] },
    "gcloudInit":           { "type":"code" },
    "gcloudGetCredentials": { "type":"code" },
    "kubectl":              { "type":"code" }
}

parser = argparse.ArgumentParser()
parser.add_argument(
  "command",
  help = "the command to run",
  choices = commands.keys() 
)
args = parser.parse_args()

if args.command in commands:
  command = commands[args.command]

  if command['type'] == "call":
    subprocess.call(command['cmd'])

  if command['type'] == "code":
    if args.command == "gcloudInit":
      gcloud = Gcloud(subprocess)
      gcloud.init()
    if args.command == "gcloudGetCredentials":
      gcloud = Gcloud(subprocess)
      gcloud.getCredentials("cluster")
    if args.command == "kubectl":
      kubernetes = Kubernetes(subprocess)
      kubernetes.kubectl()
