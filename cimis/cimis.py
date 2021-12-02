"""
Python wrapper for the CIMIS weather station API
"""

import requests
import pandas as pd

def get_stations(all=False):
    """Get station info.

    Parameters
    ----------
    all :
         (Default value = False)

    Returns
    -------

    """
    try:
        r = requests.get('http://et.water.ca.gov/api/station')
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    # parse returned data
    stations = pd.DataFrame(r.json()['Stations'])
    stations[['IsActive']] = stations[['IsActive']] == 'True'

    # active only?
    if not all:
        stations = stations[stations['IsActive']]

    return stations

def get_hourly_data():
    """Get hourly weather station data"""
    pass

def get_daily_data():
    """Get daily weather station data"""
    pass

def query_cimis():
    """Send the query to the CIMIS API"""
    pass
