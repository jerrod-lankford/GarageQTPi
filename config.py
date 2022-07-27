
import errno
import os
import uuid

import yaml

import schema


class Config(object):
    def __init__(self):
        """ Initialize config object and make sure config file exists. """
        self.raw_config = {}
        self.config = {}
        # First look for config.yaml in /config which allows us to map a volume
        # when running in docker.  If not there look in the directory the script is 
        # running from.
        location1 = "/config/config.yaml" # allows mapping a /config dir when using docker
        location2 = os.path.join(os.path.abspath(os.path.dirname(__file__)),"config.yaml") # look in script directory
        if os.path.exists(location1):
            self.file = location1
        elif os-path.exists(location2):
            self.file = location2
        else:
            raise FileNotFoundError(errno.EOENT, os.strerror(errno.ENOENT), location1 + " or " + location2) 
    
    def read(self):
        """ Reads config from disk """
        with open(self.file, 'r') as ymlfile:
            self.raw_config = yaml.load(ymlfile, Loader=yaml.FullLoader)        
    
    def write_config(self):
        """ Writes config to disk """
        with open(self.file, 'w') as ymlfile:
            yaml.dump(self.config, ymlfile)
    
    def validate(self):
        """ validates the config file against it schema. """
        self.config = schema.CONFIG_SCHEMA(self.raw_config)
        self.check_uuid()

    def get_item(self, section, name):
        """ Returns the value of a single item or None of item is not defined. """
        return(self.config.get(section,{}).get(name,None))

    def set_item(self, section, name, newvalue):
        """ Sets the value of a single item. """
        self.config["section"]["name"] = newvalue
    
    def get_section(self, section):
        """ Returns a config section or None if not defined. """
        return(self.config.get(section,None))
    
    def check_uuid(self):
        """ If Discovery is set to true make sure each door has a uuid. If not create one and update the config. """
        pass
        config_changed = False
        if self.config["mqtt"]["discovery"]:
            for door in self.config["doors"]:
                if door.get(uuid, None) is None:
                    door["uuid"] = str(uuid.uuid4())
                    config_changed = True
            if config_changed:
                self.write_config()            
    @property
    def all (self):
        return self.config










