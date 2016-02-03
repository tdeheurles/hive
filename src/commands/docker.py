import time
import sys
import string
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
        except self.subprocess.CalledProcessError:
            sys.exit(1)

    def _print_time(self, start_counter, start_date):
        end_date = time.localtime()
        end_counter = time.time()
        spent_time = end_counter - start_counter
        print "\nTimers:\n======="
        print "Start       " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", start_date)
        print "End         " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", end_date)
        print "Time spent  " + time.strftime("%M:%S +0000", time.localtime(spent_time))
        print "Real       ", spent_time
