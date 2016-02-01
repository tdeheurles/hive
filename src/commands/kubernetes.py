from gcloud import gcloud


class kubernetes:
    def __init__(self, subprocess):
        self.subprocess = subprocess
        self.cli = gcloud(subprocess).get_container() + ["kubectl"]

    def status(self, parameters):
        namespace = "--namespace=" + parameters["namespace"]
        print "\n\033[92mSERVICES\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "services", namespace])
        print "\n\033[92mRC\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "rc", namespace])
        print "\n\033[92mPODS\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "pods", namespace])
        print "\n\033[92mENDPOINTS\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "endpoints", namespace])
        print "\n\033[92mINGRESS\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "ingress", namespace])
        print "\n\033[92mNODES\n\033[0m"
        self.subprocess.check_call(self.cli + ["get", "nodes", namespace])

    def namespaces(self, parameters):
        self.subprocess.check_call(self.cli + ["get", "ns"])
