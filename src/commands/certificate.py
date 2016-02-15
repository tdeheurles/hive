import sys
from modele.Command import Command


class certificate(Command):
    def __init__(self, subprocess, hive_home, options):
        Command.__init__(self, "certificate", subprocess, hive_home, options)

    # command
    def create_ssl(self, args):
        self._verbose("create_ssl")

        domain = args["domain"]
        path = args["path"]

        key = self.hive_home + "/" + path + "/server.key"
        csr = self.hive_home + "/" + path + "/server.csr"
        crt = self.hive_home + "/" + path + "/server.crt"
        pem = self.hive_home + "/" + path + "/server.pem"

        try:
            self.subprocess.call(["openssl", "genrsa", "-out", key, "2048"])
            self.subprocess.call(["openssl", "rsa", "-in", key, "-out", key])
            self.subprocess.call(
                    ["openssl", "req", "-sha256", "-new", "-key", key,
                     "-out", csr, "-subj", "//CN=" + domain])
            self.subprocess.call(
                    ["openssl", "x509", "-req", "-days", "365",
                     "-in", csr, "-signkey", key, "-out", crt])
            self.subprocess.call(["cat " + crt + " " + key + " > " + pem], shell=True)

        except OSError as error:
            sys.exit(error)
