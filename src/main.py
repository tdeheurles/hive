import subprocess
import yaml
import importlib
from modele.Menu import Menu


stream = open("commands/commands.yml", 'r')
commands = yaml.load(stream)

menu = Menu()

args = menu.parse(commands)
commandName = args.command
commandContent = commands[args.service]["commands"][args.command]
commandType = commandContent['type']
commandParameters = commandContent["parameters"] if "parameters" in commandContent else []

parameters = {}
for parameter in commandParameters:
    sanitised = parameter["name"].replace("-", "")
    if getattr(args, sanitised) is not None:
        parameters[sanitised] = getattr(args, sanitised)

if commandType == "call":
    parameter = [getattr(args, parameter) for parameter in parameters]
    subprocess.call(commandContent['command'] + parameter)

if commandType == "code":
    module = importlib.import_module("commands." + args.service, package=None)
    service = getattr(module, args.service)(subprocess)
    result = getattr(service, commandName)(parameters)
