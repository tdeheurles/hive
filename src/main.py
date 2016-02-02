import subprocess
import yaml
import importlib
from modele.Menu import Menu


stream = open("commands/commands.yml", 'r')
commands = yaml.load(stream)

menu = Menu()

args = menu.parse(commands, "hive_service", "hive_command")

commandName = args.hive_command
commandContent = commands[args.hive_service]["commands"][args.hive_command]
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
    module = importlib.import_module("commands." + args.hive_service, package=None)
    service = getattr(module, args.hive_service)(subprocess)
    result = getattr(service, commandName)(parameters)
