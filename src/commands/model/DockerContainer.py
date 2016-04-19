import json
import collections

from DockerVolume import DockerVolume


class DockerContainer:
    def __init__(self, json_details):
        container = json.loads(json_details)[0]
        self.id = container["Id"]
        self.running = container["State"]["Running"]
        self.mounts = []
        mounts = container["Mounts"]
        for mount in mounts:
            name = mount["Name"] if "Name" in mount else None
            source = mount["Source"] if "Source" in mount else None
            destination = mount["Destination"] if "Destination" in mount else None
            driver = mount["Driver"] if "Driver" in mount else None
            mode = mount["Mode"] if "Mode" in mount else None
            rw = mount["RW"] if "Rw" in mount else None
            propagation = mount["Propagation"] if "Propagation" in mount else None

            self.mounts.append(
                DockerVolume.docker_volume_from_mounts(name, source, destination, driver, mode, rw, propagation))
