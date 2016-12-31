Ideas
=====

JSON schema
-----------

Use a JSON file at the top-level of the cache to keep track of current state of the cached data.
For example:

.. code-block:: json

    {
        "surveys": {
            "sdss": {
                "apogee": {
                    "dr13": [
                        {
                            "source": "https://data.sdss.org/sas/dr13/apogee/spectro/redux/r6/allStar-l30e.2.fits",
                            "local_name": "allStar.fits",
                            "datetime": "2016-12-31T14:57:59.227953"
                        },
                        {
                            "source": "https://data.sdss.org/sas/dr13/apogee/spectro/redux/r6/allVisit-l30e.2.fits",
                            "local_name": "allVisit.fits",
                            "datetime": "2016-12-31T15:57:59.227953"
                        }
                    ]
                }
            }
        }
    }

But the user can interface with the code instead. For example, to add a new data path from a remote_url::

    from astrodata import Cache

    with Cache() as cache:
        cache.add_data(sub_path='surveys/sdss/apogee/dr13/',
                       remote_url='https://data.sdss.org/sas/dr13/apogee/spectro/redux/r6/allStar-l30e.2.fits',
                       local_name='allStar.fits') # optional

or from an already downloaded file::

    with Cache() as cache:
        cache.add_data(sub_path='surveys/sdss/apogee/dr13/',
                       local_path='~/Downloads/allStar-v104.fits',
                       local_name='allStar.fits') # optional

The advantage of JSON is that this cache specification file can be easily passed around. So, it is
easy to build data caches on new machines automatically::

    from astrodata import Cache
    cache_schema = '/path/to/schema.json'
    Cache.build(cache_schema)

We can also validate the existing cache against the JSON schema::

    from astrodata import Cache
    with Cache() as cache:
        cache.check_state()


Command-line interface
----------------------

astrodata add https://data.sdss.org/sas/dr13/apogee/spectro/redux/r6/allStar-l30e.2.fits surveys/sdss/apogee/dr13 -n allStar.fits
astrodata add ~/Downloads/allStar-l30e.2.fits surveys/sdss/apogee/dr13 -n allStar.fits





