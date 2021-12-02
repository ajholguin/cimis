"""
Python wrapper for the CIMIS weather station API
"""

import os, requests
import pandas as pd
from datetime import date

from .util import var_name_dict

def get_stations(all: bool = False) -> pd.DataFrame:
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

    stations[['StationNbr']] = stations[['StationNbr']].astype(int)
    stations[['IsActive']] = stations[['IsActive']] == 'True'
    stations[['IsEtoStation']] = stations[['IsEtoStation']] == 'True'
    stations[['Elevation']] = stations[['Elevation']].astype(float)

    # active only?
    if not all:
        stations = stations[stations['IsActive']]

    return stations

def get_hourly_data(
        station_ids: list[int],
        variables: list[str],
        start: date,
        end: date,
        appKey: str = os.getenv('CIMIS_API_KEY')
    ) -> pd.DataFrame:
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

def query_cimis(
        station_id: int,
        variables: list[str],
        start: date,
        end: date,
        appKey: str
    ) -> pd.DataFrame:
    """Send the query to the CIMIS API"""

    payload = {
        'appKey': appKey,
        'targets': station_id,
        'startDate': start.strftime('%m-%d-%Y'),
        'endDate': end.strftime('%m-%d-%Y'),
        'dataItems': ','.join(variables),
        'unitOfMeasure': 'M'
    }

    try:
        r = requests.get('http://et.water.ca.gov/api/data', params=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    # parse returned data
    df = pd.DataFrame(r.json()['Data']['Providers'][0]['Records'])

    df[['Julian']] = df[['Julian']].astype(int)
    df[['Hour']] = df[['Hour']].astype(float) / 100
    df[['Station']] = df[['Station']].astype(int)

    # normalize variable data
    for var in variables:
        var_name = var_name_dict[var]
        var_df = pd.json_normalize(df[var_name]).add_prefix(f'{var_name}_')
        var_df[[f'{var_name}_Value']] = var_df[[f'{var_name}_Value']].astype(float)
        df = pd.concat([df.drop(columns=var_name), var_df], axis=1)

    return df
