import string
import sys
import time

from model.Command import Command
from business.FileGenerator import FileGenerator

class script(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "script", subprocess, hive_home, options)

    def hive_run(self, args):
        self._verbose("hive_run")
        start_date = time.localtime()
        start_counter = time.time()

        path = self.hive_home + "/" + args["path"]
        script_name = args["script"]
        parameters = args["parameters"]

        config_path = None
        if "config" in args:
            config_path = self.hive_home + "/" + args["config"]

        # patterns
        file_generator = FileGenerator(self.subprocess)
        added_files = file_generator.generate_hive_files(config_path, parameters, path)
        exception = None
        try:
            self.subprocess.call("cd " + path + " && ./" + script_name, shell=True)
        except OSError as error:
            exception = error
        finally:
            file_generator.cleanup(added_files, path)

        if "timed" in args:
            self._print_time(start_counter, start_date)

        if exception is not None:
            sys.exit(exception)

    def run(self, args):
        self._verbose("hive_run")
        start_date = time.localtime()
        start_counter = time.time()

        path = args["path"]
        script_name = args["script"]
        parameters = args["parameters"]
        error = None
        try:
            self.subprocess.check_call(
                ["cd " + self.hive_home + path + " && ./" + script_name + " " + string.join(parameters)],
                shell=True
            )
        except (OSError, self.subprocess.CalledProcessError) as exception:
            error = exception

        if "timed" in args:
            self._print_time(start_counter, start_date)

        if error is not None:
            sys.exit(error)

    # helpers
    def _print_time(self, start_counter, start_date):
        end_date = time.localtime()
        end_counter = time.time()
        spent_time = end_counter - start_counter
        print "\nTimers:\n======="
        print "Start       " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", start_date)
        print "End         " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", end_date)
        print "Time spent  " + time.strftime("%M:%S +0000", time.localtime(spent_time))
        print "Real       ", spent_time
