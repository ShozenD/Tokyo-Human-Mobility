import os
import numpy as np
import pandas as pd
from datetime import datetime
from key import API_LINKS, CONSUMER_KEY

def get_citycodes_by_pref(prefname = "東京都"):
    """Returns a list of citycodes for the specified prefecture"""
    citymaster = pd.read_csv('../data/citymaster.csv')
    citycode = citymaster[citymaster.prefname == prefname].loc[:,'citycode']

    return citycode

def filter_by_transport(df, transport, citycodes):
    """Filters floating population data by transportaition type"""
    targetcols = ['dailyid', 'year', 'month', 'day', 'dayofweek', 'hour', 'minute', 'latitude', 'longitude', 'citycode', 'transportation_type']
    transcodes = { 'stop': 1,'walk': 2,'bicycle': 5,'train': 7,'car': 8 } # refer to Agoop data document

    if df is None:
        raise Exception("No dataframe was passed to function!")

    if citycodes is None:
        raise Exception("Please specify citycodes!")

    if transport is None:
        raise Exception("Please specify transport type!")
    elif transport not in transcodes.keys():
        raise Exception("Invalid trasport type. Available: (stop, walk, bicycle, train, car)")

    df = df.loc[:,targetcols]
    df = df[df.citycode.isin(citycodes)]
    df = df[df.transportation_type == transcodes[transport]]

    return df

def get_data(path, start, days, prefname, transport, verbose=True):
    """Get Agoop floating population data

    Keyword arguments:
    path - Path to directory in which the data will be stored 
    start - Starting date in 'yyyy-mm-dd' format
    days - Number of days of data we want to obtain
    city - Data from which city?
    transport - Which mode of transportation
    verbose - Show progress?
    """

    citycodes = get_citycodes_by_pref(prefname=prefname)
    periods = days * 24
    df_list = []
    for timestamp in pd.date_range(start=start, periods=periods, freq='H').tolist():
        if timestamp.hour > 9: # No data available before 10 a.m. 
            datestring = datetime.strftime(timestamp, "%Y%m%d_%H")
            try:
                if verbose: print('Obtaining data from {}'.format(timestamp))

                df = pd.read_csv(API_LINKS['floatpoint']['url'].format(datestring, CONSUMER_KEY))
                df = filter_by_transport(df, transport, citycodes)
                df['datetime'] = timestamp

                if df is not None:
                    df_list.append(df) 
            except:
                continue
        if timestamp.hour == 23: # end of day
            try: 
                day = pd.concat(df_list)
                day.to_csv(os.path.join(path, '{}.csv'.format(datestring)))
                df_list = [] # empty list
            except:
                df_list = []
                continue
    
    print('Done!')