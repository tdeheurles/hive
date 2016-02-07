import sys
import yaml
import re
import os
import time
import string


class script:
    def __init__(self, subprocess):
        self.subprocess = subprocess

    def hive_run(self, args):
        path = "/currentFolder/" + args["path"]
        script_name = args["script"]
        parameters = args["parameters"]

        # read config
        config = None
        if "config" in args:
            config_path = "/currentFolder/" + args["config"]
            if not os.path.isfile(config_path):
                sys.exit("No file found at " + config_path)
            with open(config_path, 'r') as f:
                config = yaml.load(f.read())["spec"]

        # patterns
        added_files = self.generate_hive_files(config, parameters, path)
        exception = None
        try:
            self.subprocess.call("cd " + path + " && ./" + script_name, shell=True)
        except OSError as error:
            exception = error
        finally:
            self.cleanup(added_files, path)

        if exception is not None:
            sys.exit(exception)

    def generate_hive_files(self, config, parameters, path):
        added_files = []
        for pattern_file in [f for f in os.listdir(path) if f[:5] == "hive."]:
            with open(path + "/" + pattern_file, 'r') as stream:
                pattern = stream.read()

            matches = re.findall("<%.*?%>", pattern, re.MULTILINE)
            for match in matches:
                def configuration_error(message):
                    self.cleanup(added_files, path)
                    if message is None:
                        message = "No configuration match for parameter " + match + " in file " + pattern_file
                    sys.exit(message)

                file_parameter = match.translate(None, '<% >').split('.')
                value = config
                for i in range(len(file_parameter)):
                    key = file_parameter[i]
                    if key == "args":
                        cli_parameter_position, error = self._cli_parameter(file_parameter, parameters)
                        if error is not None:
                            self.cleanup(added_files, path)
                            sys.exit(error.format(match, pattern_file))
                        value = parameters[cli_parameter_position]
                        break
                    else:
                        if value is None:
                            configuration_error("Please, rerun with the config parameter")
                        try:
                            if key not in value.keys():
                                configuration_error(None)
                            value = value[key]
                        except AttributeError:
                            configuration_error(None)
                try:
                    pattern = pattern.replace(match, str(value))
                except TypeError as error:
                    print error
                    configuration_error(None)

            new_name = pattern_file[5:]
            added_files.append(new_name)
            with open(path + "/" + new_name, 'w') as stream:
                stream.write(pattern)

        return added_files

    def run(self, args):
        start_date = time.localtime()
        start_counter = time.time()

        path = args["path"]
        script_name = args["script"]
        parameters = args["parameters"]
        error = None
        try:
            self.subprocess.check_call(
                ["cd /currentFolder" + path + " && ./" + script_name + " " + string.join(parameters)],
                shell=True
            )
        except (OSError, self.subprocess.CalledProcessError) as exception:
            error = exception

        if "timed" in args:
            self._print_time(start_counter, start_date)

        if error is not None:
            sys.exit(error)

    def cleanup(self, added_files, path):
        for new_file in added_files:
            os.remove(path + "/" + new_file)

    def _cli_parameter(self, file_parameter, parameters):
        # case of cli parameter

        error = None
        cli_parameter_position = None

        if len(file_parameter) <= 1:
            error = "incorrect hive parameter for {0} in file {1}"
            return cli_parameter_position, error
        try:
            cli_parameter_position = parameters.index(file_parameter[1]) + 1
        except ValueError:
            error = "incorrect hive cli parameter for {0} in file {1}. No key value given"

        if len(parameters) <= cli_parameter_position:
            error = "incorrect hive number of parameter for {0} in file {1}"
            return cli_parameter_position, error

        return cli_parameter_position, error

    def _print_time(self, start_counter, start_date):
        end_date = time.localtime()
        end_counter = time.time()
        spent_time = end_counter - start_counter
        print "\nTimers:\n======="
        print "Start       " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", start_date)
        print "End         " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", end_date)
        print "Time spent  " + time.strftime("%M:%S +0000", time.localtime(spent_time))
        print "Real       ", spent_time
