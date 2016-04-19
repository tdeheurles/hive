class DockerVolume:
    def __init__(self, name, source, destination, driver, mode, rw, propagation):
        self.name = name
        self.source = source
        self.destination = destination
        self.driver = driver
        self.mode = mode
        self.rw = rw
        self.propagation = propagation

    @staticmethod
    def docker_volume_from_mounts(name, source, destination, driver, mode, rw, propagation):
        return DockerVolume(name, source, destination, driver, mode, rw, propagation)

    @staticmethod
    def docker_volume_from_cli(driver, name):
        return DockerVolume(name, None, None, driver, None, None, None)
