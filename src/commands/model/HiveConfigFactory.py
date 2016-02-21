import sys
import yaml
from HiveConfig import HiveConfig


class HiveConfigFactory(object):

    @staticmethod
    def create(hive_config_path):
        try:
            with open(hive_config_path + "/hive.yml", "r") as stream:
                yaml_content = stream.read()

        except IOError as error:
            sys.exit(error)

        content = yaml.load(yaml_content)

        return HiveConfig(content, hive_config_path)
