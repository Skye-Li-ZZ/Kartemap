# -*- coding: utf-8 -*-
"""
BUS 216F-1, Spring 2021
Python and Applications to Business Analytics II

Project: Dash Application - Kartemap

Zhizun(Skye) Li
"""

import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

## Created my own database using former data file
CITY_DATA = 'data_Skye\\city.csv'
AIRPORT_DATA = 'data_Skye\\airport.csv'
AIRLINES_DATA = 'data_Skye\\airlines.csv'
ROUTES_DATA = 'data_Skye\\routes.csv'

TRACE = False

# load dataframe for cities
#
if TRACE:
    print('CITIES')
city_df = pd.read_csv(CITY_DATA, header=None)
city_df.columns = ['City']
if TRACE:
    print(city_df.shape)
    print(city_df)

# load dataframe for airports
#
if TRACE:
    print('AIRPORTS')
airport_df = pd.read_csv(AIRPORT_DATA, header=None)
airport_df.columns = ['Airport_id', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone', 'type', 'Source']
if TRACE:
    print('Pass 1: All Airports', airport_df.shape)

airport_df['Airport_id'] = pd.to_numeric(airport_df['Airport_id'])
## I don't understand r'\N' here.
airport_df.drop(airport_df[airport_df['Airport_id'] == r'\N'].index, inplace=True)
## Changed to China
airport_df.drop(airport_df[airport_df['Country'] != 'China'].index, inplace=True)
if TRACE:
    print('Pass 2: Only China Airports', airport_df.shape)

city_names = list(city_df['City'])
airport_df = airport_df[airport_df['City'].isin(city_names)]
if TRACE:
    print('Pass 3: Only Airports in the Cities list', airport_df.shape)
    print(airport_df)

# load dataframe for routes
#
if TRACE:
    print('ROUTES')
routes_df = pd.read_csv(ROUTES_DATA, header=None)
routes_df.columns = ['Airline', 'Airline_id', 'Source_airport', 'Source_airport_id', 'Destination_airport', 'Destination_airport_id', 'Codeshare', 'Stops', 'Equipment']
if TRACE:
    print(1, routes_df.shape)

routes_df.drop(routes_df[routes_df['Airline_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Source_airport_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Destination_airport_id'] == r'\N'].index, inplace=True)
if TRACE:
    print(2, routes_df.shape)

routes_df.drop(routes_df[routes_df['Stops'] != 0].index, inplace=True)
if TRACE:
    print(3, routes_df.shape)

routes_df['Airline_id'] = pd.to_numeric(routes_df['Airline_id'])
routes_df['Source_airport_id'] = pd.to_numeric(routes_df['Source_airport_id'])
routes_df['Destination_airport_id'] = pd.to_numeric(routes_df['Destination_airport_id'])

airport_ids = list(airport_df['Airport_id'])
routes_df = routes_df[routes_df['Source_airport_id'].isin(airport_ids)]
routes_df = routes_df[routes_df['Destination_airport_id'].isin(airport_ids)]

if TRACE:
    print(4, routes_df.shape)
    print(routes_df)

# load dataframe for airlines
#
if TRACE:
    print('AIRLINES')
airlines_df = pd.read_csv(AIRLINES_DATA, header=None)
airlines_df.columns = ['Airline_id', 'Name', 'Alias', 'IATA', 'ICAO', 'Callsign', 'Country', 'Active']
if TRACE:
    print(1, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Airline_id'] == r'\N'].index, inplace=True)
airlines_df['Airline_id'] = pd.to_numeric(airlines_df['Airline_id'])
if TRACE:
    print(2, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Active'] != 'Y'].index, inplace=True)
if TRACE:
    print(3, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Country'] != 'China'].index, inplace=True)
if TRACE:
    print(4, airlines_df.shape)
    print(airlines_df)

# if __name__ == '__main__':
#     pass
