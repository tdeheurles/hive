class SubProject:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.actions = []
        self.kubernetes = []

    def add_action(self, action):
        self.actions += action

    def add_kubernetes_resource(self, resource):
        self.kubernetes.append(resource)

