from itertools import chain

import numpy as np

from Orange.data import Table
from Orange.data.domain import filter_visible


LATITUDE_NAMES = ('latitude', 'lat')
LONGITUDE_NAMES = ('longitude', 'lng', 'long', 'lon')


def find_lat_lon(data, filter_hidden=False):
    """
    Infer latitude and longitude attributes from data

    - If there are less than two numeric variables, return None, None
    - If there are variables with recognized names (see LATITUDE_NAMES,
      LONGITUDE_NAMES), return them
    - Otherwise, if there are exactly two numeric variables
       - if one has a matching name, the other is chosen to be the other coord
       - if one has all values below 90 and the other has at least one above,
        these are latitude and longitude
       - otherwise, the first one is latitude, the other is longitude
    - Otherwise (there are more than two variables), return a pair containing
      the first variable twice, so the user sees a diagonal, which indicates
      that this has to be set manually.
    """
    assert isinstance(data, Table)

    cont_vars = (var for var in chain(data.domain.variables, data.domain.metas)
                 if var.is_continuous)
    if filter_hidden:
        cont_vars = filter_visible(cont_vars)
    cont_vars = list(cont_vars)

    if len(cont_vars) < 2:
        return None, None

    lat_attr = next(
        (attr for attr in cont_vars
         if attr.name.lower().startswith(LATITUDE_NAMES)), None)
    lon_attr = next(
        (attr for attr in cont_vars
         if attr.name.lower().startswith(LONGITUDE_NAMES)), None)
    if lat_attr and lon_attr:
        return lat_attr, lon_attr

    def max_in_col(attr):
        if not data:
            return 0
        return np.nanmax(np.abs(data.get_column_view(attr)[0].astype(float)))

    if len(cont_vars) == 2:
        if lat_attr is not None:
            lon_attr = cont_vars[1 - cont_vars.index(lat_attr)]
        elif lon_attr is not None:
            lat_attr = cont_vars[1 - cont_vars.index(lon_attr)]
        else:
            for lat_attr, lon_attr in (cont_vars[::-1], cont_vars):
                if max_in_col(lat_attr) <= 90 < max_in_col(lon_attr):
                    break
            if max_in_col(lon_attr) > 180:
                lat_attr = lon_attr = cont_vars[0]
    else:
        lat_attr = lon_attr = cont_vars[0]

    return lat_attr, lon_attr
