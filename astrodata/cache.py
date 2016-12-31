# Standard library
from collections import defaultdict
import datetime
import json
import os
import shutil
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

__all__ = ['cache']

class Cache(object):
    """
    A class that maintains the cache path structure.
    """
    def __init__(self, config_file=None):

        if config_file is None:
            config_file = '~/.astrodataconfig'

        astrodata_config_path = os.path.expanduser(config_file)
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

        self._schema_path = os.path.join(self.root, 'schema.json')

        # create empty JSON file if nothing exists
        if not os.path.exists(self._schema_path):
            with open(self._schema_path, 'w') as f:
                f.write(json.dumps({}))

        with open(self._schema_path, 'r') as f:
            self.schema = json.loads(f.read())

    def close(self):
        with open(self._schema_path, 'r+') as f:
            f.write(json.dumps(self.schema, indent=4, sort_keys=True))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def add_data(self, sub_path, url_or_path, local_name=None, **kwargs):
        """
        Add a data file to the cache.

        This is a destructive process for existing files -- the file will be moved
        from its current directory to the cache. If a file already exists at the
        specified ``sub_path`` with the same name, it will be over-written.

        Parameters
        ----------
        sub_path : str
            Path to save the file relative to the cache root.
        url_or_path : str
            The URL of the file to download or a local path to the already downloaded
            data file.
        local_name : str (optional)
            The filename to save this file as locally. Default is to grab the
            basename of the remote URL.
        **kwargs
            All other keyword arguments are passed to `~astrodata.download.download_file`.

        """

        full_cache_path = os.path.join(self.root, sub_path)
        if not os.path.exists(full_cache_path):
            os.makedirs(full_cache_path)

        if os.path.exists(url_or_path):
            if local_name is None:
                local_name = os.path.basename(url_or_path)
            local_path = os.path.join(full_cache_path, local_name)
            shutil.move(url_or_path, local_path)

        else:
            from .download import download_file
            local_path = download_file(url_or_path, full_cache_path, filename=local_name, **kwargs)
            local_name = os.path.basename(local_path)

        # get each path level as a list of names
        path_pieces = os.path.normpath(sub_path).split(os.sep)

        sub_schema = self.schema
        for piece in path_pieces:
            sub_schema[piece] = sub_schema.get(piece, dict())
            sub_schema = sub_schema[piece]

        sub_schema[local_name] = dict()
        sub_schema[local_name]['source'] = url_or_path
        sub_schema[local_name]['download_datetime'] = datetime.datetime.now().isoformat()

        return local_path

    def check_state(self):
        pass

    @classmethod
    def build(self, cache_spec_file):
        pass

cache = Cache()
