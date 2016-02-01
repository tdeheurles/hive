import subprocess
import yaml
import importlib
from modele.Parser import Parser

stream = open("commands/commands.yml", 'r')
commands = yaml.load(stream)

mainName = "main"
serviceName = "service"

parsers = {
    mainName: Parser(prog='hive')
}

subparsers = {
    serviceName: parsers[mainName].add_subparsers(title=serviceName, dest="service")
}

for commandName in commands:
    command = commands[commandName]
    parsers[commandName] = subparsers[serviceName].add_parser(commandName, help=command["help"])
    subparsers[commandName] = parsers[commandName].add_subparsers(
        title="commands",
        dest="command"
    )

    for subCommandName in command["commands"]:
        subCommand = command["commands"][subCommandName]
        parsers[subCommandName] = subparsers[commandName].add_parser(
            subCommandName,
            help=subCommand["help"]
        )

        if "parameters" in subCommand:
            for parameters in subCommand["parameters"]:
                name = parameters["name"]
                doc = parameters["help"]
                if "action" in parameters:
                    parsers[subCommandName].add_argument(
                        name,
                        help=doc,
                        action=parameters["action"],
                        const=name
                    )

                else:
                    parsers[subCommandName].add_argument(name, help=doc)

args = parsers[mainName].parse_args()

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
