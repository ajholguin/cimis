"""
Python wrapper for the CIMIS weather station API
"""

import os, requests
import pandas as pd
from datetime import date
from typing import Union

from .util import var_name_dict

def get_stations(all: bool = False) -> pd.DataFrame:
    """Get station info.

    Parameters
    ----------
    all: bool : All stations? (or just active)
         (Default value = False)

    Returns
    -------
    stations: pd.DataFrame
    
    """

    r = requests.get('http://et.water.ca.gov/api/station')
    r.raise_for_status()
    if r.content.startswith(b'<html><head><title>Request Rejected</title></head>'):
        raise Exception('CIMIS Server Error')
    
    # parse returned data
    stations = pd.DataFrame(r.json()['Stations'])

    stations['StationNbr'] = stations['StationNbr'].astype(int)
    stations['ConnectDate'] = pd.to_datetime(stations['ConnectDate'], format="%m/%d/%Y")
    stations['DisconnectDate'] = pd.to_datetime(stations['DisconnectDate'], format="%m/%d/%Y")
    stations['IsActive'] = stations['IsActive'] == 'True'
    stations['IsEtoStation'] = stations['IsEtoStation'] == 'True'
    stations['Elevation'] = stations['Elevation'].astype(float)

    # active only?
    if not all:
        stations = stations[stations['IsActive']]

    return stations

def get_hourly_data(
        station_id: int,
        variables: list[str],
        start: date,
        end: date,
        appKey: str = None
    ) -> pd.DataFrame:
    """Get hourly weather station data

    Parameters
    ----------
    station_id: int : Station ID/number
        
    variables: list[str] : Variables to return
        
    start: date : Start date
        
    end: date : End date
        
    appKey: str : API Key
         (Default value = os.getenv('CIMIS_API_KEY'))

    Returns
    -------
    cimis_data: pd.DataFrame

    """

    appKey = appKey if appKey else os.getenv('CIMIS_API_KEY')

    cimis_data = query_cimis(station_id, variables, start, end, appKey)

    return cimis_data

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
    """Send the query to the CIMIS API

    Parameters
    ----------
    station_id: int : Station ID/number
        
    variables: list[str] : Variables to return
        
    start: date : Start date
        
    end: date : End date
        
    appKey: str : API Key
        

    Returns
    -------
    df: pd.DataFrame

    """

    if isinstance(variables, pd.Series):
        variables = variables.tolist()

    payload = {
        'appKey': appKey,
        'targets': station_id,
        'startDate': start.strftime('%m-%d-%Y'),
        'endDate': end.strftime('%m-%d-%Y'),
        'dataItems': ','.join(variables),
        'unitOfMeasure': 'E'
    }

    r = requests.get(
        'http://et.water.ca.gov/api/data',
        params=payload,
        timeout=15      # seconds
    )
    r.raise_for_status()
    if r.content.startswith(b'<html><head><title>Request Rejected</title></head>'):
        raise Exception('CIMIS Server Error')
    
    # parse returned data
    df = pd.DataFrame(r.json()['Data']['Providers'][0]['Records'])
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Julian'] = df['Julian'].astype(int)
    df['Hour'] = df['Hour'].astype(float) / 100
    df['Station'] = df['Station'].astype(int)

    # normalize variable data
    for var in variables:
        var_name = var_name_dict[var]
        var_df = pd.json_normalize(df[var_name]).add_prefix(f'{var_name}_')
        var_df[f'{var_name}_Value'] = var_df[f'{var_name}_Value'].astype(float)
        df = pd.concat([df.drop(columns=var_name), var_df], axis=1)

    return df
