import sys


class ExecutionListFactory(object):
    @classmethod
    def extract(cls, hive_file_content):
        if "executionLists" not in hive_file_content["spec"]:
            return {}

        content_execution_lists = hive_file_content["spec"]["executionLists"]

        results = {}
        for execution_list in content_execution_lists:
            if "name" not in execution_list:
                sys.exit("One of your execution list have no `name` key")
            name = execution_list["name"]
            if name not in results:
                results[name] = {}

            if "actions" not in execution_list:
                sys.exit("One executionList with name " + name + " have no `actions` key")
            actions = execution_list["actions"]

            if "services" not in execution_list:
                sys.exit("executionList named " + name + " with keys " + str(actions) + " have no `services` key")
            services = execution_list["services"]

            for action in actions:
                if action in results[name]:
                    sys.exit("There is two executionLists with name `" + name + "` and action `" + action + "`")
                results[name][action] = services

        return results
