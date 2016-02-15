class KubernetesPod:
    def __init__(self, name, ready, status, restarts, age):
        self.name = name
        self.ready = ready
        self.status = status
        self.restarts = restarts
        self.age = age

    @staticmethod
    def pods_from_api_call(call):
        pods = []
        for line in call.split('\n')[1:-1]:
            args = line.split()
            pods.append(KubernetesPod(args[0], args[1], args[2], args[3], args[4]))
        return pods

    def __str__(self):
        return self.name + " " + self.ready + " " + self.status + " " + self.restarts + " " + self.age
