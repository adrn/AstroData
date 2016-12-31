from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Standard library
import os
import shutil
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

# Third-party
from astropy.extern.six.moves import urllib
from astropy.tests.helper import remote_data, pytest
import numpy as np

# Package
from ..cache import Cache

def _check_schema(cache, sub_path, local_name):
    sub_schema = cache.schema
    for piece in sub_path.split('/'):
        assert piece in sub_schema
        sub_schema = sub_schema[piece]

    assert 'source' in sub_schema[local_name]
    assert 'download_datetime' in sub_schema[local_name]

def add_data_helper(config_path, repo_path, data_path):

    # this is an arbitrary choic:
    sub_path = 'sdss/apogee/dr13'

    # --------------------------------------------------------------------
    # without specifying local name
    #
    with Cache(config_path) as cache:
        local_path = cache.add_data(sub_path, data_path)
        local_name = os.path.basename(local_path)

    with Cache(config_path) as cache:
        _check_schema(cache, sub_path, local_name)
        assert cache.schema['sdss']['apogee']['dr13'][local_name]['source'] == data_path

    shutil.rmtree(repo_path)

    # --------------------------------------------------------------------
    # specifying local name
    #
    with Cache(config_path) as cache:
        local_name = 'bob'
        cache.add_data(sub_path,
                       data_path,
                       local_name=local_name)

    with Cache(config_path) as cache:
        _check_schema(cache, sub_path, local_name)
        assert cache.schema['sdss']['apogee']['dr13'][local_name]['source'] == data_path

    shutil.rmtree(repo_path)

    # --------------------------------------------------------------------
    # overwrite
    #
    with Cache(config_path) as cache:
        cache.add_data(sub_path,
                       data_path,
                       local_name=local_name)

    with Cache(config_path) as cache:
        cache.add_data(sub_path,
                       data_path,
                       local_name=local_name)

    with Cache(config_path) as cache:
        _check_schema(cache, sub_path, local_name)
        assert len(cache.schema['sdss']['apogee']['dr13']) == 1

    # --------------------------------------------------------------------
    # make sure the schema is not modified if download fails
    #
    if 'http' in data_path:
        with pytest.raises(urllib.error.URLError):
            with Cache(config_path) as cache:
                cache.add_data(sub_path,
                               os.path.join(os.path.split(data_path)[0], 'nonexistentfile'),
                               local_name='alice')
    else:
        with pytest.raises(ValueError):
            with Cache(config_path) as cache:
                cache.add_data(sub_path,
                               os.path.join(os.path.split(data_path)[0], 'nonexistentfile'),
                               local_name='alice')

    with Cache(config_path) as cache:
        _check_schema(cache, sub_path, local_name)
        assert len(cache.schema['sdss']['apogee']['dr13']) == 1

    shutil.rmtree(repo_path)

    # --------------------------------------------------------------------
    # add two
    #
    with Cache(config_path) as cache:
        cache.add_data(sub_path,
                       data_path,
                       local_name='bob')

    with Cache(config_path) as cache:
        cache.add_data(sub_path,
                       data_path,
                       local_name='alice')

    with Cache(config_path) as cache:
        _check_schema(cache, sub_path, 'bob')
        _check_schema(cache, sub_path, 'alice')
        assert len(cache.schema['sdss']['apogee']['dr13']) == 2

class TestCache(object):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = str(tmpdir)
        self.config_path = str(tmpdir.join('.testconfig'))
        self.repo_path = str(tmpdir.join('astrodata'))

        conf = ConfigParser()
        conf.add_section('astrodata')
        conf.set('astrodata', 'repository_path', self.repo_path)

        # Writing our configuration file to 'example.cfg'
        with open(self.config_path, 'w') as configfile:
            conf.write(configfile)

    def test_init(self):
        with Cache(self.config_path) as cache:
            assert os.path.exists(cache.root)

        cache = Cache()
        assert os.path.exists(cache.root)
        cache.close()

    @remote_data
    def test_add_remote_data(self):
        data_path = 'http://www.astropy.org'
        add_data_helper(self.config_path, self.repo_path, data_path)

    def test_add_local_data(self):
        # make a local "data file"
        data_file = os.path.join(self.tmpdir, 'test-data.dat')
        np.savetxt(data_file, np.random.random(size=(128,5)))
        assert os.path.exists(data_file)

        add_data_helper(self.config_path, self.repo_path, data_file)
