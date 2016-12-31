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
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data, pytest

# Package
from ..cache import Cache

def _check_schema(cache, sub_path, local_name):
    sub_schema = cache.schema
    for piece in sub_path.split('/'):
        assert piece in sub_schema
        sub_schema = sub_schema[piece]

    assert 'source' in sub_schema[local_name]
    assert 'download_datetime' in sub_schema[local_name]

class TestCache(object):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
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

        sub_path = 'sdss/apogee/dr13'

        # --------------------------------------------------------------------
        # without specifying local name
        #
        with Cache(self.config_path) as cache:
            local_path = cache.add_data(sub_path, 'http://www.astropy.org')
            local_name = os.path.basename(local_path)

        with Cache(self.config_path) as cache:
            _check_schema(cache, sub_path, local_name)
            assert cache.schema['sdss']['apogee']['dr13'][local_name]['source'] == 'http://www.astropy.org'

        shutil.rmtree(self.repo_path)

        # --------------------------------------------------------------------
        # specifying local name
        #
        with Cache(self.config_path) as cache:
            local_name = 'bob'
            cache.add_data(sub_path,
                           'http://www.astropy.org',
                           local_name=local_name)

        with Cache(self.config_path) as cache:
            _check_schema(cache, sub_path, local_name)
            assert cache.schema['sdss']['apogee']['dr13'][local_name]['source'] == 'http://www.astropy.org'

        shutil.rmtree(self.repo_path)

        # --------------------------------------------------------------------
        # overwrite
        #
        with Cache(self.config_path) as cache:
            cache.add_data(sub_path,
                           'http://www.astropy.org',
                           local_name=local_name)

        with Cache(self.config_path) as cache:
            cache.add_data(sub_path,
                           'http://www.astropy.org',
                           local_name=local_name)

        with Cache(self.config_path) as cache:
            _check_schema(cache, sub_path, local_name)
            assert len(cache.schema['sdss']['apogee']['dr13']) == 1

        # --------------------------------------------------------------------
        # make sure the schema is not modified if download fails
        #
        with pytest.raises(urllib.error.URLError):
            with Cache(self.config_path) as cache:
                cache.add_data(sub_path,
                               'http://www.astropy.org/nonexistentfile',
                               local_name='alice')

        with Cache(self.config_path) as cache:
            _check_schema(cache, sub_path, local_name)
            assert len(cache.schema['sdss']['apogee']['dr13']) == 1

        shutil.rmtree(self.repo_path)

        # --------------------------------------------------------------------
        # add two
        #
        with Cache(self.config_path) as cache:
            cache.add_data(sub_path,
                           'http://www.astropy.org',
                           local_name='bob')

        with Cache(self.config_path) as cache:
            cache.add_data(sub_path,
                           'http://www.astropy.org',
                           local_name='alice')

        with Cache(self.config_path) as cache:
            _check_schema(cache, sub_path, 'bob')
            _check_schema(cache, sub_path, 'alice')
            assert len(cache.schema['sdss']['apogee']['dr13']) == 2

    # def test_add_local_data(self):
    #     with Cache(self.config_path) as cache:
    #         cache.add_data() # TODO

    #     # TODO: make sure the schema is not modified if download fails
    #     # with Cache() as cache:
    #     #     cache.add_data()
