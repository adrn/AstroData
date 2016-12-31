# -*- coding: utf-8 -*-

""" Note: This is a modified version of astropy/astropy/utils/tests/test_data.py """

# Licensed under a 3-clause BSD style license - see licenses/ASTROPY.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Standard library
import os

# Third-party
from astropy.extern.six.moves import urllib
from astropy.tests.helper import remote_data, pytest

# Package
from ..cache import cache
from ..download import download_file

TESTURL = 'http://www.astropy.org'
download_dir = cache.root
tmp_filename = 'test-delete'

@remote_data
def test_download_cache():
    # Download the test URL and make sure it exists, then clear just that
    # URL and make sure it got deleted.
    tmp_path = os.path.join(download_dir, tmp_filename)
    fnout = download_file(TESTURL, cache_path=download_dir, filename=tmp_filename)
    assert os.path.isdir(download_dir)
    assert os.path.isfile(fnout)
    os.unlink(tmp_path)
    assert not os.path.exists(fnout)

    # Try with a sub_path that doesn't exist
    tmp_path = os.path.join(download_dir, 'test', tmp_filename)
    fnout = download_file(TESTURL, cache_path=os.path.join(download_dir, 'test'),
                          filename=tmp_filename)
    assert os.path.isdir(download_dir)
    assert os.path.isfile(fnout)
    os.unlink(tmp_path)
    os.rmdir(os.path.join(download_dir, 'test'))
    assert not os.path.exists(fnout)

    # Try existing file
    tmp_path = os.path.join(download_dir, tmp_filename)
    fnout = download_file(TESTURL, cache_path=download_dir, filename=tmp_filename)
    assert os.path.isdir(download_dir)
    assert os.path.isfile(fnout)

    fnout = download_file(TESTURL, cache_path=download_dir, filename=tmp_filename)
    assert os.path.isfile(fnout)

    fnout = download_file(TESTURL, cache_path=download_dir, filename=tmp_filename, overwrite=True)
    assert os.path.isfile(fnout)

    os.unlink(tmp_path)
    assert not os.path.exists(fnout)

@remote_data
def test_download_noprogress():

    tmp_path = os.path.join(download_dir, tmp_filename)
    fnout = download_file(TESTURL, cache_path=download_dir, filename=tmp_filename, show_progress=False)
    assert os.path.isdir(download_dir)
    assert os.path.isfile(fnout)
    os.unlink(tmp_path)
    assert not os.path.exists(fnout)

@remote_data
def test_invalid_location_download():
    """
    checks that download_file gives a URLError and not an AttributeError,
    as its code pathway involves some fiddling with the exception.
    """

    with pytest.raises(urllib.error.URLError):
        download_file('http://astropy.org/nonexistentfile', cache_path=download_dir)

def test_invalid_location_download_noconnect():
    """
    checks that download_file gives an IOError if the socket is blocked
    """

    # This should invoke socket's monkeypatched failure
    with pytest.raises(IOError):
        download_file('http://astropy.org/nonexistentfile', cache_path=download_dir)
