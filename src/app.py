import os
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from config import (alert_help, hourly_file, left_bound, mapbox_token,
                    paragraph_1, paragraph_2, right_bound, seasons_file,
                    stations_file)
from plots import get_mapbox_plot, get_rose_plot, get_scatter_plot

# Buttons ids for Bikes section
button_ids = ['spring_button', 'summer_button', 'autumn_button']

# Load data needed for plots
station_names = pd.read_csv(stations_file)["departure_name"].sort_values()
seasons = pd.read_csv(seasons_file, index_col=0)
hours = pd.read_csv(hourly_file)
data_table = pd.read_csv(stations_file)

with open(alert_help) as alert, open(paragraph_1) as par_1, open(paragraph_2) as par_2:
    alert = alert.readlines()
    par_1 = par_1.readlines()
    par_2 = par_2.readlines()

data_table.rename(columns={
    'departure_name': 'Station Name', 'departure_latitude': 'Latitude',
    'departure_longitude': 'Longitude', 'count': 'Count', 'traffic': 'Traffic'
}, inplace=True)

data_table['Traffic'] = pd.Categorical(
    data_table['Traffic'], categories=[
        'very low', 'low', 'moderate', 'high', 'very high'
    ], ordered=True)


# Paths and themes
external_stylesheets = [dbc.themes.SKETCHY]
assets_path = os.getcwd() + '/assets'

px.set_mapbox_access_token(open(mapbox_token).read())

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_folder=assets_path,
    suppress_callback_exceptions=True
)

app.layout = dbc.Container([
    dcc.Store(id="store"),
    html.H1("Helsinki City Bikes Dashboard"),
    html.Hr(),
    dbc.Tabs([
        dbc.Tab(label="Stations", tab_id="stations"),
        dbc.Tab(label="Bikes", tab_id="bikes"),
        dbc.Tab(label='Data Table', tab_id='data_tab'),
        dbc.Tab(label='About', tab_id='about')
    ],
        id="tabs",
        active_tab="stations",
    ),
    html.Br(),
    html.Div(
        id="tab-content", className="p-4")
])


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and data is not None:
        if active_tab == "bikes":
            return bikeslayout
        elif active_tab == "stations":
            return stationslayout
        elif active_tab == "about":
            return aboutlayout
        elif active_tab == "data_tab":
            return data_table
        else:
            return "This dashboard is currently being developed."


@app.callback(Output("store", "data"), [Input("store", "data")])
def generate_graphs(n):
    """
    This callback generates three simple graphs from random data.
    """
    if not n:
        # generate empty graphs when app loads
        return {k: go.Figure(data=[]) for k in ["bikes", "hist_1", "hist_2"]}

    # simulate expensive graph generation process
    time.sleep(2)

    # generate 100 multivariate normal samples
    data = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], 100)

    scatter = go.Figure(
        data=[go.Scatter(x=data[:, 0], y=data[:, 1], mode="markers")]
    )
    hist_1 = go.Figure(data=[go.Histogram(x=data[:, 0])])
    hist_2 = go.Figure(data=[go.Histogram(x=data[:, 1])])

    # save figures in a dictionary for sending to the dcc.Store
    return {"bikes": scatter, "hist_1": hist_1, "hist_2": hist_2}


@app.callback(
    [Output(x, 'n_clicks') for x in button_ids],
    [Output(x, 'active') for x in button_ids],
    Output('rose_plot', 'figure'),
    [Input(x, 'n_clicks') for x in button_ids])
def button_active(spring_clicks, summer_clicks, autumn_clicks):
    if spring_clicks != 0:
        fig = get_rose_plot(season='spring')
        return [0, 0, 0, True, False, False, fig]
    elif summer_clicks != 0:
        fig = get_rose_plot(season='summer')
        return [0, 0, 0, False, True, False, fig]
    elif autumn_clicks != 0:
        fig = get_rose_plot(season='autumn')
        return [0, 0, 0, False, False, True, fig]
    else:
        fig = get_rose_plot(season='spring')
        return [0, 0, 0, True, False, False, fig]


@app.callback(
    Output('distance_widget', 'value'),
    Output('duration_widget', 'value'),
    Output('gauge_widget', 'value'),
    Output('thermometer_widget', 'value'),
    [Input(x, 'active') for x in button_ids]
)
def widget_change(spring_active, summer_active, autumn_active):
    if spring_active:
        return list(seasons.loc['spring'].values)
    elif summer_active:
        return list(seasons.loc['summer'].values)
    elif autumn_active:
        return list(seasons.loc['autumn'].values)
    else:
        return [0, 0, 0, 0]


@app.callback(
    Output('dropdown', 'value'),
    Output('hour_chart', 'figure'),
    Input('range_slider', 'value'),
    Input('dropdown', 'value')
)
def hour_graph(range, station):
    left, right = range
    fig = get_scatter_plot(station, left, right, hours)
    return station, fig


# ------------
# STATION LAYOUT
# ------------


dropdown = dcc.Dropdown(
    id='dropdown',
    options=[
        {'label': i, 'value': i} for i in station_names
    ],
    multi=False,
    value=station_names.iloc[0]
)

station_search_button = html.Div([
    dbc.Input(id="input", placeholder="Station...", type="text"),
    html.Br(),
    html.P(id="output")
])

station_chart_slider = html.Div([
    dcc.RangeSlider(
        id='range_slider',
        min=0,
        max=24,
        step=1,
        value=[left_bound, right_bound],
        marks={0: '0:00', 6: '6:00', 12: '12:00', 18: '18:00', 24: '24:00'}
    ),
    html.Div(id='output-container-range-slider')
])

stationslayout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Departures by station"),
            dropdown,
            dcc.Graph(figure=get_scatter_plot(
                station_names.iloc[0], left_bound, right_bound, hours
            ), id='hour_chart'),
            station_chart_slider
        ],
            width=4),
        dbc.Col([
            html.H3("Helsinki stations map"),
            dcc.Graph(figure=get_mapbox_plot()),
        ], width=8),
    ]),
])


# ------------
# BIKES LAYOUT
# ------------


speed = daq.Gauge(
    id='gauge_widget',
    color={
        "gradient": True, "ranges": {
            "#07BC07": [0, 10],
            "#FFFF00": [10, 20],
            "#FB5F5F": [20, 30]
        }},
    value=0,
    min=0,
    labelPosition='top',
    label={'label': "Avg. Speed (km/h)", 'style': {'font-size': 25}},
    max=30
)

termo = daq.Thermometer(
    id='thermometer_widget',
    color='#D796EE',
    value=0,
    min=(-5),
    max=25,
    labelPosition='top',
    label={
        'label': "Avg. Temperature (°C)",
        'style': {
            'font-size': 25
        }},
    style={
        'margin-bottom': '5%'
    }
)

duration = daq.LEDDisplay(
    id='duration_widget',
    label={'label': "Avg. Duration (s)", 'style': {'font-size': 25}},
    labelPosition='top',
    value=0,
    color='#28435c'
)

distance = daq.LEDDisplay(
    id='distance_widget',
    label={
        'label': "Avg. Distance (m)",
        'style': {
            'font-size': 25
        }},
    labelPosition='top',
    value=0,
    color='#009eb0'
)

bikeslayout = dbc.Row([
    dbc.Col([
        dbc.Row([
            dbc.Col(width=3),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("Spring", color="primary", active=True,
                               outline=True, id="spring_button", n_clicks=0),
                    dbc.Button("Summer", color="primary", active=False,
                               outline=True, id="summer_button", n_clicks=0),
                    dbc.Button("Autumn", color="primary", active=False,
                               outline=True, id="autumn_button", n_clicks=0)
                ],
                    size="lg",
                    className="mr-1",
                    id='buttons_season'
                )],
                width=9
            ),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(speed, width=6),
            dbc.Col(termo, width=6)]),
        dbc.Row([
            dbc.Col(duration, width=6),
            dbc.Col(distance, width=6)]),
    ],
        width=6),
    dbc.Col([
        html.H3("Distance Plot"),
        dcc.Graph(figure=get_rose_plot(), id='rose_plot')
    ])
]),


# ------------
# DATA TABLE LAYOUT
# ------------


table = dash_table.DataTable(
    id='table-multicol-sorting',
    data=data_table.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in data_table.columns],
    virtualization=True,
    editable=False,
    page_size=100,
    sort_action='native',
    sort_mode='single',
    fixed_rows={'headers': True},
    style_cell={
        'minWidth': '15px', 'width': '15px', 'maxWidth': '30px',
        'whiteSpace': 'normal',
        'height': 'auto',
        'lineHeight': '20px',
        'overflow': 'ellipsis',
        'textOverflow': 'ellipsis',
        'textAlign': 'center'
    }
)

data_table = html.Div([
    dbc.Col([
        html.H3("Data Table"),
        table
    ], width=12),
])


# ------------
# ABOUT LAYOUT
# ------------


aboutlayout = html.Div([
    html.H4("What are Helsinki City bikes?"),
    html.P(par_1),
    dbc.Alert(alert, color="primary"),
    html.P(par_2),
    html.H4("Dataset"),
    dcc.Link('Helsinki City Bikes on Kaggle.com', refresh=True,
             href='https://www.kaggle.com/geometrein/helsinki-city-bikes'),

    html.H4("Authors"),
    html.P("Jerzy Łukaszewicz & Marek Szydłowski")
])


if __name__ == "__main__":
    app.run_server(debug=False, port=8888)
