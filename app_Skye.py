# -*- coding: utf-8 -*-
"""
BUS 216F-1, Spring 2021
Python and Applications to Business Analytics II

Project: Dash Application - Kartemap

Zhizun(Skye) Li
"""

from operator import itemgetter
import pandas as pd
import math

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

# drop down list for use in airport codes
from controls_Skye import city_df, airlines_df, routes_df, airport_df


# setup app with stylesheets
app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
## Changed the theme to 'Darkly'; just to play around to get familiar with dbc.themes module

# Create map template
mapbox_access_token =    'pk.eyJ1Ijoic2t5ZWwiLCJhIjoiY2tuaDY4dGVzMGo0aDJvcWg5M2t6dWxvMiJ9.9gM3DQlljDR33BBHyX8DYg'
## Changed the token with my default public token(is it?), though not quite sure about what it is and the normal way to find this


## This is the map; Changed the geographic center
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=5, r=5, b=5, t=5),
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        center=dict(lon=103.23, lat=35.33),
        zoom=2,
    ),
)

## This is the card on LHS
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Start City', className='text-danger'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='start-city',
                    disabled=False
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Start City Airport', className='text-danger'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='start-city-airport',
                    disabled=True
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Destination City', className='text-danger'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='destination-city',
                    disabled=False
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Destination City Airport', className='text-danger'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in city_df['City']],
                    value='',
                    id='destination-city-airport',
                    disabled=True
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Airline', className='text-danger'),
                dcc.Dropdown(
                    options=[{'label': col, 'value': col} for col in airlines_df['Name']],
                    value='',
                    id='airline',
                    disabled=True
                ),
            ]
        ),
        
        dbc.Button('Find Route',
                   id='find-route-button',
                   outline=True, className='mr-1'),
        
        dbc.FormText(
            id='distance'
            ),
               
    ],

    body=True,
)

## This is how these parts are formatted; imagine it like a table (that's smart!!!)
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H2(), md=3),
                dbc.Col(
                    html.H2('Kartemap - Flight Route Analysis',
                            className='text-white'), md=9
                )
            ], align='center', className='bg-info'),
        dbc.Row(
            [
                dbc.Col(controls, md=3),
                dbc.Col(dcc.Graph(id='map'), md=9),
            ],
            align='center', className='bg-info',
        ),
        ## Not sure if we need to add more lines here?
        
        dbc.Row(
            [
                dbc.Col(dash_table.DataTable(
                    id='shortest-path-table'), md=12),
            ],
            align='center', className='bg-info',
        ),
        
        dbc.Row(
            [
                dbc.Col(html.H2(), md=3),
                dbc.Col(
                    html.H6('Copyright (C) 2021, Brandeis University Course: Python and Applications to Business Analytics II, All Rights Reserved.', className='text-white'), md=9
                )
            ], align='center', className='bg-info'),

    ],
    id='main-container',
    style={'display': 'flex', 'flex-direction': 'column'},
    fluid=True
)

"""
It makes more sense to select start-city & airport and destination-city & ariport first, then decide the airline.
"""

# start or destination city selected, populate start or destination airport
#
@app.callback([Output('start-city-airport', 'options'),
               Output('start-city-airport', 'disabled')],
              [Input('start-city', 'value')])
def populate_source_airport_controls_after_start_city_selected(start_city):
    if start_city == '':
        start_city_airport_options = []
        start_city_airport_disable = True
    else:
        # retrieve all airport_ids for a given source city
        source_airport_ids = airport_df.query(f'City=="{start_city}"')['Airport_id'].tolist()
        
        # get all source airports
        ctl_src_airport_df = airport_df[airport_df['Airport_id'].isin(source_airport_ids)]
        start_city_airport_options = [{'label': col, 'value': col} for col in ctl_src_airport_df['Name']]
        start_city_airport_disable = False
    return start_city_airport_options, start_city_airport_disable
        
@app.callback([Output('destination-city-airport', 'options'),
               Output('destination-city-airport', 'disabled')],
              [Input('destination-city', 'value')])
def populate_destination_airport_controls_after_start_city_selected(destination_city):
    if destination_city == '':
        destination_city_airport_options = []
        destination_city_airport_disable = True
    else:
        # retrieve all airport_ids for a given destination city
        destination_airport_ids = airport_df.query(f'City=="{destination_city}"')['Airport_id'].tolist()
        
        # get all destination airports
        ctl_dst_airport_df = airport_df[airport_df['Airport_id'].isin(destination_airport_ids)]
        destination_city_airport_options = [{'label': col, 'value': col} for col in ctl_dst_airport_df['Name']]
        destination_city_airport_disable = False        
    return destination_city_airport_options, destination_city_airport_disable
       

# start and destination airport selected, populate and enable airline controls
#
@app.callback([Output('airline', 'options'),
               Output('airline', 'disabled')],
              [Input('start-city-airport', 'value'),
               Input('destination-city-airport', 'value')])
def populate_airline_controls_after_aiports_selected(source_airport, destination_airport):
    if source_airport == '' or destination_airport == '':
        return [], True
    else:
        source_airport_id = airport_df.query(f'Name == "{source_airport}"')["Airport_id"].to_list()[0]
        source_airport_airlines = routes_df.query(f'Source_airport_id == "{source_airport_id}"')["Airline_id"].to_list()
        destination_airport_id = airport_df.query(f'Name == "{destination_airport}"')["Airport_id"].to_list()[0]
        destination_airport_airlines = routes_df.query(f'Destination_airport_id == "{destination_airport_id}"')["Airline_id"].to_list()
        
        common_airlines = list(set(source_airport_airlines).intersection(destination_airport_airlines))
        
        airline_options = []
        for i in common_airlines:
            ctl_route_df = routes_df.copy()
            ctl_airline_df = airlines_df.copy()
            iata = ctl_route_df.query(f'Airline_id == "{i}"')["Airline"].to_list()[0]
            try:
                option = ctl_airline_df.query(f'IATA == "{iata}"')["Name"].to_list()[0]
            except:
                option = iata
            
            airline_options.append(option)
            
            ctl_airline_option_df = airlines_df[airlines_df['Name'].isin(airline_options)]
            airline = [{'label': col, 'value': col} for col in ctl_airline_option_df['Name']]


        return airline, False

# draw the map
@app.callback(Output('map', 'figure'),
              [Input('start-city', 'value'),
               Input('destination-city', 'value')],
              [State('map', 'relayoutData')])
def make_map(start_city, destination_city, map_layout):
    traces = []
    for name, df in airport_df.groupby('City'):
        trace = dict(
            type='scattermapbox',
            lon=df['Longitude'],
            lat=df['Latitude'],
            text=df['City'],
            showlegend=False,
            marker=dict(
                size=10 if name in [start_city, destination_city] else 5,
                opacity=0.95 if name in [start_city, destination_city] else 0.65,
                symbol='circle',
                color='red' if name in [start_city, destination_city] else 'blue',
            ),
            visible=True
        )
        traces.append(trace)

    # relayoutData is None by default, and {'autosize': True} without relayout action
    if map_layout is not None:
        if 'mapbox.center' in map_layout.keys():
            lon = float(map_layout['mapbox.center']['lon'])
            lat = float(map_layout['mapbox.center']['lat'])
            zoom = float(map_layout['mapbox.zoom'])
            layout['mapbox']['center']['lon'] = lon
            layout['mapbox']['center']['lat'] = lat
            layout['mapbox']['zoom'] = zoom

    figure = dict(data=traces, layout=layout)
    return figure

"""
@app.callback(Output('shortest-path-table', 'data'),
              [Input('start-city-airport', 'value'),
               Input('destination-city-airport', 'value')])
"""

@app.callback(Output('distance', 'children'),
              [Input('start-city-airport', 'value'),
               Input('destination-city-airport', 'value')])

def find_shortest_route(start_city_airport, destination_city_airport):
    
    lat1 = airport_df.query(f'Name == "{start_city_airport}"')["Latitude"].to_list()[0]
    lat2 = airport_df.query(f'Name == "{destination_city_airport}"')["Latitude"].to_list()[0]
    lon1 = airport_df.query(f'Name == "{start_city_airport}"')["Longitude"].to_list()[0]
    lon2 = airport_df.query(f'Name == "{destination_city_airport}"')["Longitude"].to_list()[0]
    
    phi_1 = lat1 * math.pi / 180.0
    phi_2 = lat2 * math.pi / 180.0
    change_phi = (lat2 - lat1) * math.pi / 180
    change_lambda = (lon2 - lon1) * math.pi / 180

    a = math.sin(change_phi / 2.0) * math.sin(change_phi / 2.0) + math.cos(phi_1) * math.cos(phi_2) * math.sin(change_lambda / 2.0) * math.sin(change_lambda / 2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    dist_km = 6371.0 * c

    
    return f"Distance(km): {dist_km}"
    s

if __name__ == '__main__':
    app.run_server(debug=True)
