# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
CFMIP utility functions.
"""
__docformat__ = "epytext"


def getCfmipSiteDetails(minSiteNo=1, maxSiteNo=119, coordFileURL=None, hasHeight=False):
    """
    Read CFMIP2 site numbers, names and lat-long coordinates from a URL. If a URL isn't specified the
    following default location is used: http://cfmip.metoffice.com/cfmip2/pointlocations.txt

    It is assumed that the file contains records ordered by site number, and that the latter increase
    in monotonic fashion without gaps (though this function should work even if they're not). It is
    further assumed that each record contains, by default, the 4 comma-separated fields: site-number,
    longitude, latitude, 'site-name'. If the hasHeight argument is set True then each record is
    expected to contain the 5 fields: site-number, longitude, latitude, height, 'site-name'.

    Longitude coordinates are adjusted to be in the range 0 - 360 degs. Latitude coordinates are not
    adjusted.

    @param minSiteNo: The minimum site number. Sites with IDs below this value are excluded from the returned lists.
    @type  minSiteNo: int
    @param maxSiteNo: The maximum site number. Sites with IDs above this value are excluded from the returned lists.
    @type  maxSiteNo: int
    @param coordFileURL: The URL of the web page or text file which contains CFMIP2 site details.
    @type  coordFileURL: string
    @param hasHeight: Set to True if the source file contains height values in the fourth column.
    @type  hasHeight: boolean

    @return: the 4-element tuple ([ids], [lats], [lons], [names]) or, if hasHeight is True, the
       5-element tuple ([ids], [lats], [lons], [hts], [names])

    @raise IOError: Raised if the requested or default URL cannot be opened.
    """
    from urllib.request import urlopen

    defaultURL = 'http://cfmip.metoffice.com/cfmip2/pointlocations.txt'
    url = coordFileURL or defaultURL
    doc = urlopen(url)

    # Initialise return lists.
    ids = []
    lats = []
    lons = []
    hts = []
    names = []

    # Loop over records in URL resource, skipping records where siteno outside range minSiteNo - maxSiteNo.
    for bline in doc.readlines():
        line = bline.decode()
        if hasHeight:
            (siteno, lon, lat, ht, name) = line[:-1].split(',', 4)
        else:
            (siteno, lon, lat, name) = line[:-1].split(',', 3)
        siteno = int(siteno)
        if siteno < minSiteNo or siteno > maxSiteNo:
            continue
        ids.append(siteno)
        lats.append(float(lat))
        lon = float(lon)
        if lon < 0:
            lon += 360
        if lon >= 360:
            lon -= 360
        lons.append(lon)
        if hasHeight:
            hts.append(float(ht))
        names.append(name.strip(" '"))

    # Close the URL
    doc.close()

    if hasHeight:
        return ids, lats, lons, hts, names
    else:
        return ids, lats, lons, names
