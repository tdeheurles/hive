class KubernetesNamespace:
    def __init__(self, name, label, status, age):
        self.name = name
        self.label = label
        self.status = status
        self.age = age

    @staticmethod
    def namespaces_from_api_call(call):
        namespaces = []
        for line in call.split('\n')[1:-1]:
            args = line.split()
            namespaces.append(KubernetesNamespace(args[0], args[1], args[2], args[3]))
        return namespaces

    def __str__(self):
        return self.name + " " + self.label + " " + self.status + " " + self.age
