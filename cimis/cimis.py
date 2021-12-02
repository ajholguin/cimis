"""
Python wrapper for the CIMIS weather station API
"""

import os, requests
import pandas as pd
from .util import to_title_case

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

def get_hourly_data(station_ids, variables, start, end, appKey=os.getenv('CIMIS_API_KEY')):
    """Get hourly weather station data"""
    cimis_data = []
    for station_id in station_ids:
        df = query_cimis(station_id, variables, start, end, appKey)
        df.insert(0, 'station_id', station_id)
        cimis_data.append(df)
    return pd.concat(cimis_data)

def get_daily_data():
    """Get daily weather station data"""
    pass

def query_cimis(station_id, variables, start, end, appKey):
    """Send the query to the CIMIS API"""
    payload = {
        'appKey': appKey,
        'targets': station_id,
        'startDate': start,
        'endDate': end,
        'dataItems': ','.join(variables),
        'unitOfMeasure': 'M'
    }
    try:
        r = requests.get('http://et.water.ca.gov/api/data', params=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    # parse returned data
    df = pd.DataFrame(r.json()['Data']['Providers'][0]['Records'])

    for var in variables:
        var_name = to_title_case(var)
        var_df = pd.json_normalize(df[var_name]).add_prefix(f'{var_name}_')
        df = pd.concat([df.drop(columns=var_name), var_df], axis=1)

    return df
