import argparse
import subprocess

def getDockerVolumes(): 
  volumes = subprocess.check_output(["docker", "volume", "ls"]).split('\n')
  return volumes

commands = {
    "dps":    { "type":"call", "cmd": ["docker", "ps"] },
    "dim":    { "type":"call", "cmd": ["docker", "images"] },
    "dvl":    { "type":"call", "cmd": ["docker", "volume", "ls"] },
    "gcloud": { "type":"code"}
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
    if args.command == "gcloud":
      # get volumes
      volumes = getDockerVolumes()
      # if no volume with name gcloud_cache
      #   create volume gcloud
      #   gcloud init
      print volumes
