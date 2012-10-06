import yaml

class Config(object):
    def __init__(self, conf_loc="aplomb.conf"):
        conf_file = open("aplomb.conf") # XXX: location for dev only
        self.conf_dict = yaml.load("".join(conf_file.readlines()))
        conf_file.close()

        self._uuid = None

    @property
    def conf_server(self):
        return self.conf_dict['conf_server']

    @property
    def uuid_file(self):
        return self.conf_dict['uuid_file']

    @property
    def uuid(self):
        if self._uuid is None:
            ufile = open(self.uuid_file)
            uuid = ufile.readlines()[0].strip()
            self._uuid = uuid
            ufile.close()
        return self._uuid

    @property
    def openssl_conf(self):
        return self.conf_dict['openssl_conf']

    @property
    def client_crt(self):
        return self.conf_dict['client_crt']
