import argparse
import subprocess
from Gcloud import gcloud
from modele.Volume import Volume
from modele.Docker import getDockerVolume

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
    gcloud()

