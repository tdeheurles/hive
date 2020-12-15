import sys
from model.Command import Command


class deployer(Command):
    def __init__(self, subprocess, hive_home, options):
        pass

    # commands
    def describe(self, args):
        print args["id"]
