# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import os
import time

import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Label import Label
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import dash_table
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from dash_bootstrap_components._components.Container import Container


# TODO: Move to main
stations = pd.read_csv("data/stations.csv", index_col=0)
stations = stations["Name"]

data = pd.read_csv('data/dataframe.csv')
data = data.rename(columns={'departure_name':'Station Name','departure_latitude':'Latitude','departure_longitude':'Longitude','count':'Count','traffic':'Traffic'})

# Paths and themes
external_stylesheets = [dbc.themes.SKETCHY]
assets_path = os.getcwd() + '/assets'


app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_folder=assets_path
)

app.layout = dbc.Container([
    dcc.Store(id="store"),
    html.H1("Helsinki City Bikes Dashboard"),
    html.Hr(),
    dbc.Tabs([
        dbc.Tab(label="Bikes", tab_id="bikes"),
        dbc.Tab(label="Stations", tab_id="stations"),
        dbc.Tab(label='About', tab_id='about'),
        dbc.Tab(label='Help', tab_id='help')
    ],
        id="tabs",
        active_tab="bikes",
    ),
    html.Br(),
    html.Div(
        id="tab-content", className="p-4"),
])

button_group = html.Div(
    [
        dbc.RadioItems(
            id="radios",
            className="btn-group",
            labelClassName="btn btn-secondary",
            labelCheckedClassName="active",
            options=[
                {"label": "Spring", "value": 1},
                {"label": "Summer", "value": 2},
                {"label": "Autumn", "value": 3},
                {"label": "Winter", "value": 4},
            ],
            value=1,
        ),
        html.Div(id="output"),
        html.Br(),
    ],
    className="radio-group",
)

station_search_button = html.Div(
    [
        dbc.Input(id="input", placeholder="Station..", type="text"),
        html.Br(),
        html.P(id="output"),
    ]
)

bikeslayout = html.Div([
    dbc.Row([
        dbc.Col(html.Div("Test"), width=6),
        dbc.Col([
            dbc.Row(button_group),
            dbc.Row([
                dbc.Col(html.Div("Test"), width=6),
                dbc.Col(html.Div("Test"), width=6)
            ]),
            dbc.Row([
                dbc.Col(html.Div("Test"), width=6),
                dbc.Col(html.Div("Test"), width=6)
            ]),
        ], 
        width=6,
        align="center",
        ),
        ]),
    ])


table = dash_table.DataTable(
    data = data.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in data.columns],
    virtualization=True,
    editable=False,
    row_selectable="single",
    page_size= 100,
    fixed_rows={'headers': True},
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'lineHeight': '15px'
    }
)


dropdown = dcc.Dropdown(
    options=[
        {'label': i, 'value': i} for i in stations
    ],
    multi=False
)  

stationslayout = html.Div([
    dbc.Row([
        dbc.Col([
            dropdown,
            html.Br(),
            table
        ], width=8),
        dbc.Col([
            dbc.Row("TEST"),
            dbc.Row("TEST"),
        ], width=4),
    ]),
])

helplayout = html.Div()

with open('data/alerthelp.txt') as a, open('data/paragraph1help.txt') as p1, open('data/paragraph2help.txt') as p2:
    alert = a.readlines()
    p1 = p1.readlines()
    p2 = p2.readlines()

# TODO: Load text from file
aboutlayout = html.Div([
    html.H4("What are Helsinki City bikes?"),
    html.P(p1),
    dbc.Alert(alert, color="primary"),
    html.P(p2),
    html.H4("Dataset"),
    dcc.Link('Helsinki City Bikes on Kaggle.com', refresh=True,
             href='https://www.kaggle.com/geometrein/helsinki-city-bikes?fbclid=IwAR2v2jyT8aG1q1tEz61AGcezpBrm85zuiUV-d9uPgLY8Xr9Ly86JhEWNTg0'),

    html.H4("Authors"),
    html.P("Jerzy Łukaszewicz & Marek Szydłowski")
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


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)