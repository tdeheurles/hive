import yaml
import sys
import re
import os


class FileGenerator:
    def __init__(self, subprocess):
        self.subprocess = subprocess

    # public
    def generate_hive_files(self, config_path, parameters, path):
        def configuration_error(message):
            self.cleanup(added_files, path)
            if message is None:
                message = "No configuration match for parameter " + match + " in file " + pattern_file
            sys.exit(message)

        def control_key_in_value(value, key):
            try:
                if key not in value.keys():
                    configuration_error("key: " + key + " not found in configuration, please, rerun with the config parameter")
                value = value[key]
            except AttributeError:
                configuration_error(None)
            return value

        config = self._open_config(config_path)

        added_files = []
        for pattern_file in [f for f in os.listdir(path) if f[:5] == "hive."]:
            with open(path + "/" + pattern_file, 'r') as stream:
                pattern = stream.read()

            matches = re.findall("<%.*?%>", pattern, re.MULTILINE)
            for match in matches:

                file_parameter = match.translate(None, '<% >').split('.')
                value = config
                # progress in the config yaml
                for i in range(len(file_parameter)):
                    key = file_parameter[i]

                    # CLI parameters
                    if key == "args":
                        cli_parameter_position, error = self._cli_parameter(file_parameter, parameters)
                        if error is not None:
                            self.cleanup(added_files, path)
                            sys.exit(error.format(match, pattern_file))
                        value = parameters[cli_parameter_position]
                        break

                    # base64 file transpilation
                    if key == "__b64__":
                        control_key_in_value(value, key)
                        value = self._extract_base64(value[key], config_path)
                        break

                    # No configuration for parameter
                    if value is None:
                        configuration_error(
                                "No config for key: " + match + \
                                "in file " + pattern_file + \
                                ", add a configuration file with --config")

                    # continue to read yaml tree
                    value = control_key_in_value(value, key)

                try:
                    pattern = pattern.replace(match, str(value))
                except TypeError as error:
                    print error
                    configuration_error(None)

            new_name = pattern_file[5:]
            added_files.append(new_name)
            with open(path + "/" + new_name, 'w') as stream:
                stream.write(pattern)

            self.subprocess.call(["chmod", "755", path + "/" + new_name])
        return added_files

    def _open_config(self, config_path):
        config = None
        if config_path is not None:
            if not os.path.isfile(config_path):
                sys.exit("No file found at " + config_path)
            with open(config_path, 'r') as f:
                config = yaml.load(f.read())["spec"]
        return config

    def cleanup(self, added_files, path):
        for new_file in added_files:
            os.remove(path + "/" + new_file)

    # helpers
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

    def _extract_base64(self, file_path, config_path):

        content_path = os.path.dirname(config_path) + "/" + file_path

        try:
            base64_content = self.subprocess.check_output(
                ["base64", "-i", "-w", "0", content_path]
            )
        except OSError as error:
            sys.exit(error)

        return base64_content
