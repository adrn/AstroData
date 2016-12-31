# Standard library
import os
from os.path import abspath, join, split, exists
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

__all__ = ['cache']

class Cache(object):
    """
    A class that maintains the cache path structure.
    """
    def __init__(self):

        astrodata_config_path = os.path.expanduser('~/.astrodataconfig')
        if not os.path.exists(astrodata_config_path):
            raise IOError("AstroData config file at ~/.astrodataconfig does not exist!")

        # parse the config file to read the repository path
        astrodata_conf = ConfigParser()
        astrodata_conf.read([astrodata_config_path])

        astrodata_metadata = dict(astrodata_conf.items('astrodata'))
        repo_path = astrodata_metadata.get('repository_path', None)

        if repo_path is None:
            raise ValueError("Failed to read repository path from the ~/.astrodataconfig file!")

        self.root = os.path.abspath(os.path.expanduser(repo_path))
        if not os.path.exists(self.root):
            os.makedirs(self.root)

cache = Cache()
