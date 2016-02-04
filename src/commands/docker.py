import string
import sys
import time

from DockerVolume import DockerVolume


class docker:
    def __init__(self, subprocess):
        self.subprocess = subprocess
        self._cli = ["docker"]

    # commands
    def cli(self, args):
        command = args["parameters"] if "parameters" in args else []
        self._execute_command(command)

    def run(self, args):
        start_date = time.localtime()
        start_counter = time.time()

        path = args["path"]
        script = args["script"]
        parameters = args["parameters"]
        error = None
        try:
            self.subprocess.check_call(
                ["cd /currentFolder" + path + " && ./" + script + " " + string.join(parameters)],
                shell=True
            )
        except (OSError, self.subprocess.CalledProcessError) as exception:
            error = exception

        if "timed" in args:
            self._print_time(start_counter, start_date)

        if error is not None:
            sys.exit(error)

    def build(self, args):
        path = "/currentFolder/" + args["path"]
        script = args["script"]
        parameters = args["parameters"]

        # read config
        import yaml
        with open("/currentFolder/" + args["config"], 'r') as f:
            config = yaml.load(f.read())["spec"]

        # patterns
        import os
        import re
        added_files = []
        for pattern_file in [f for f in os.listdir(path) if f[:5] == "hive."]:
            with open(path + "/" + pattern_file, 'r') as stream:
                pattern = stream.read()

            matches = re.findall("<%.*?%>", pattern, re.MULTILINE)
            for match in matches:
                arg = match.translate(None, '<% >').split('.')

                value = config
                for i in range(len(arg)):
                    key = arg[i]
                    if key == "args":
                        value = parameters[parameters.index(arg[i+1]) + 1]
                        break
                    else:
                        value = value[key]

                pattern = pattern.replace(match, value)

            new_name = pattern_file[5:]
            added_files.append(new_name)
            with open(path + "/" + new_name, 'w') as stream:
                stream.write(pattern)

        # run new script
        exception = None
        try:
            self.subprocess.call("cd " + path + " && ./" + script, shell=True)
        except OSError as error:
            exception = error
        finally:
            for new_file in added_files:
                os.remove(path + "/" + new_file)

        if exception is not None:
            sys.exit(exception)

    # public
    def get_docker_volumes(self):
        volumes_string = self.subprocess.check_output(["docker", "volume", "ls"]).split('\n')[1:-1]
        volumes = []
        for line in volumes_string:
            args = line.split()
            volumes.append(DockerVolume(args[0], args[1]))
        return volumes

    # helpers
    def _execute_command(self, command):
        try:
            self.subprocess.check_call(self._cli + command)
        except self.subprocess.CalledProcessError as error:
            sys.exit(error.errnu)

    def _print_time(self, start_counter, start_date):
        end_date = time.localtime()
        end_counter = time.time()
        spent_time = end_counter - start_counter
        print "\nTimers:\n======="
        print "Start       " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", start_date)
        print "End         " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", end_date)
        print "Time spent  " + time.strftime("%M:%S +0000", time.localtime(spent_time))
        print "Real       ", spent_time
