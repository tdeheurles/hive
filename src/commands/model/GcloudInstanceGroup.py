class GcloudInstanceGroup:
    def __init__(self, name, zone, base_instance_name, size, target_size, instance_template, autoscale):
        self.name = name
        self.zone = zone
        self.base_instance_name = base_instance_name
        self.size = size
        self.target_size = target_size
        self.instance_template = instance_template
        self.autoscale = autoscale

    @staticmethod
    def instance_group_from_api_call(call):
        instances = []
        for line in call.split('\n')[1:-1]:
            args = line.split()
            instances.append(GcloudInstanceGroup(args[0], args[1], args[2], args[3], args[4], args[5], args[6]))
        return instances

    def __str__(self):
        return self.name + " " + \
               self.zone + " " + \
               self.size + " " + \
               self.target_size + " " + \
               self.instance_template + " " + \
               self.autoscale
