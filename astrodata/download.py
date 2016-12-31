""" Utilities for downloading and caching files """

from __future__ import division, print_function

# Standard library
import os
import sys
import contextlib
import io
import shutil
import socket
import tempfile

# Third party
import astropy.units as u
from astropy.utils.data import check_free_space_in_dir
from astropy.utils.console import ProgressBarOrSpinner
from astropy.extern.six.moves import urllib

# Package
from .path import cache

def download_file(remote_url, sub_path, filename=None, timeout=10.*u.second,
                  show_progress=True, block_size=2**16, overwrite=False):
    """
    This is a modified version of `~astropy.utils.data.download_file` that
    allows the user to specify the cache path.

    Accepts a URL, downloads and caches the result returning the local filename.

    Parameters
    ----------
    remote_url : str
        The URL of the file to download
    sub_path : str
        The sub-path, relative to the root astrodata cache, to save the file.
    filename : str (optional)
        The filename to save this file as, locally. Default is to grab the
        basename of the remote URL.
    timeout : `~astropy.units.Quantity` (optional)
        The timeout as an Astropy Quantity (default is 10 seconds).
    show_progress : bool (optional)
        Display a progress bar during the download (default is ``True``).
    block_size : int (optional)
        The download block size (default is 64K, 2**16).
    overwrite : bool (optional)
        Overwrite file if it exists (default is ``False``).

    Returns
    -------
    local_path : str
        Returns the local path that the file was download to.

    """

    timeout_s = timeout.to(u.second).value
    cache_path = os.path.join(cache.root, sub_path)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    if filename is None:
        filename = os.path.basename(remote_url)

    local_path = os.path.join(cache_path, filename)

    if os.path.exists(local_path) and not overwrite:
        return local_path

    try:
        with contextlib.closing(urllib.request.urlopen(remote_url, timeout=timeout_s)) as remote:
            # get file info
            info = remote.info()
            if 'Content-Length' in info:
                try:
                    size = int(info['Content-Length'])
                except ValueError:
                    size = None
            else:
                size = None

            if size is not None:
                check_free_space_in_dir(cache_path, size)

            # show progress via stdout, or just output to stringIO and ignore
            if show_progress:
                progress_stream = sys.stdout
            else:
                progress_stream = io.StringIO()

            # message to display when downloading file:
            dlmsg = "Downloading {0}".format(remote_url)
            with ProgressBarOrSpinner(size, dlmsg, file=progress_stream) as p:
                with tempfile.NamedTemporaryFile(dir=cache_path, delete=False) as f:
                    try:
                        bytes_read = 0
                        block = remote.read(block_size)
                        while block:
                            f.write(block)
                            bytes_read += len(block)
                            p.update(bytes_read)
                            block = remote.read(block_size)

                    except BaseException:
                        if os.path.exists(f.name):
                            os.remove(f.name)
                        raise

            shutil.move(f.name, local_path)

    except urllib.error.URLError as e:
        if hasattr(e, 'reason') and hasattr(e.reason, 'errno') and e.reason.errno == 8:
            e.reason.strerror = e.reason.strerror + '. requested URL: ' + remote_url
            e.reason.args = (e.reason.errno, e.reason.strerror)
        raise e
    except socket.timeout as e:
        # this isn't supposed to happen, but occasionally a socket.timeout gets
        # through.  It's supposed to be caught in `urrlib2` and raised in this
        # way, but for some reason in mysterious circumstances it doesn't. So
        # we'll just re-raise it here instead
        raise urllib.error.URLError(e)

    return local_path
