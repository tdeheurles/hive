class ManifestFactory:
    def __init__(self):
        pass

    def new_namespace(self, args):
        if "name" not in args:
            return {}

        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": args["name"]
            }
        }

        if "project" in args:
            namespace["metadata"]["labels"] = {}
            namespace["metadata"]["labels"]["project"] = args["project"]

        if "subproject" in args:
            namespace["metadata"]["labels"]["subproject"] = args["subproject"]

        return namespace
