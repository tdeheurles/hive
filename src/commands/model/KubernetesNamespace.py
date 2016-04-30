class KubernetesNamespace:
    def __init__(self, name, status, age):
        self.name = name
        self.status = status
        self.age = age

    @staticmethod
    def namespaces_from_api_call(call):
        namespaces = []
        for line in call.split('\n')[1:-1]:
            args = line.split()
            namespaces.append(KubernetesNamespace(args[0], args[1], args[2]))
        return namespaces

    def __str__(self):
        return self.name + " " + self.status + " " + self.age
