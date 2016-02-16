import sys


class Command:
    def __init__(self, name, subprocess, hive_home, options):
        self.verboseMode = True if "verbose" in options else False
        self.subprocess = subprocess
        self.hive_home = hive_home
        self.options = options
        self._verbose(name)

    def _verbose(self, message):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

        # following from Python cookbook, #475186
        def has_colours(stream):
            if not hasattr(stream, "isatty"):
                return False
            if not stream.isatty():
                return False  # auto color only on TTYs
            try:
                import curses
                curses.setupterm()
                return curses.tigetnum("colors") > 2
            except:
                # guess false in case of error
                return False

        has_colours = has_colours(sys.stdout)

        def printout(text, colour=WHITE):
            if has_colours:
                seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m\n"
                sys.stdout.write(seq)
            else:
                sys.stdout.write(text)

        if self.verboseMode:
            printout("hive-python: " + message, BLUE)
