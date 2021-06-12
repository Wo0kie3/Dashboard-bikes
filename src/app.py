# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import os
import time

from dash_html_components.Br import Br
from utils import file_exists
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Label import Label
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import dash_table
import dash_daq as daq
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from dash_bootstrap_components._components.Container import Container
from plots import get_rose_plot
from config import Season, stations_file, seasons_file, hourly_file, mapbox_token


# TODO: Move to main
stations = pd.read_csv(stations_file)

stations = stations["departure_name"]

seasons = pd.read_csv(seasons_file, index_col=0)

hours = pd.read_csv(hourly_file)

data = pd.read_csv('data/stations.csv')
data = data.rename(columns={'departure_name': 'Station Name', 'departure_latitude': 'Latitude',
                   'departure_longitude': 'Longitude', 'count': 'Count', 'traffic': 'Traffic'})
data['Traffic'] = pd.Categorical(data['Traffic'],
                                 categories=['very low', 'low',
                                             'moderate', 'high', 'very high'],
                                 ordered=True
                                 )
# Paths and themes
external_stylesheets = [dbc.themes.SKETCHY]
assets_path = os.getcwd() + '/assets'

# Map

mapa_data = pd.read_csv(stations_file)

mapa_data.replace({'traffic': {
    'very high': 'Very high',
    'high': 'High',
    'moderate': 'Moderate',
    'low': 'Low',
    'very low': 'Very low'
}}, inplace=True)

px.set_mapbox_access_token(open(mapbox_token).read())

mapa = px.scatter_mapbox(
    mapa_data, lat='departure_latitude', lon='departure_longitude',
    size='count', color='traffic', text='departure_name', zoom=10,
    template='plotly', mapbox_style='basic', labels={'traffic': "Traffic:"}
)

mapa.update_traces(
    hovertemplate="%{text}<br>(%{lat}, %{lon})<br><extra></extra>"
)

mapa.update_layout(
    mapbox=dict(
        center=go.layout.mapbox.Center(
            lat=60.19525,
            lon=24.9013
        )
    ),
    margin={"r": 0, "t": 00, "l": 0, "b": 0}
)

#


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
        id="tab-content", className="p-4"),
])

card_content = [
    dbc.CardHeader("Card header"),
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text",
            ),
        ]
    ),
]

help_tab = html.Div([
    dbc.Row(
        [
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
        ],
        className="mb-4",
    ),

    dbc.Row(
        [
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
            dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
        ],
        className="mb-4",
    )
])


station_search_button = html.Div(
    [
        dbc.Input(id="input", placeholder="Station..", type="text"),
        html.Br(),
        html.P(id="output"),
    ]
)

duration = daq.LEDDisplay(
    id='my_duration',
    label={'label':"Avg. Duration (s)", 'style':{'font-size':25}},
    labelPosition='top',
    value=0,
    color='#28435c'
)

gauge = daq.Gauge(
    id='my_gauge',
    color={"gradient": True, "ranges": {"#07BC07": [
        0, 10], "#FFFF00": [10, 20], "#FB5F5F": [20, 30]}},
    value=0,
    min=0,
    labelPosition='top',
    label={'label':"Avg. Speed (km/h)", 'style':{'font-size':25}},
    max=30
)

termo = daq.Thermometer(
    id='my_thermometer',
    color='#D796EE',
    value=0,
    min=(-5),
    max=25,
    labelPosition='top',
    label={'label':"Avg. Temperature (°C)", 'style':{'font-size':25}},
    style={
        'margin-bottom': '5%'
    }
)

distance = daq.LEDDisplay(
    id='my_distance',
    label={'label':"Avg. Distance (m)", 'style':{'font-size':25}},
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
                )
            ], width=9),
        ]),
        html.Br(),
        dbc.Row([
                dbc.Col(gauge, width=6),
                dbc.Col(termo, width=6)
                ]),
        dbc.Row([
                dbc.Col(duration, width=6),
                dbc.Col(distance, width=6)
                ]),
    ],
        width=6,
    ),
    dbc.Col([
        html.H3("Distance Plot"),
        dcc.Graph(figure=get_rose_plot(), id='rose_plot')
    ])
]),

button_ids = ['spring_button', 'summer_button', 'autumn_button']


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
    Output('my_distance', 'value'),
    Output('my_duration', 'value'),
    Output('my_gauge', 'value'),
    Output('my_thermometer', 'value'),
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


table = dash_table.DataTable(
    id='table-multicol-sorting',
    data=data.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in data.columns],
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

dropdown = dcc.Dropdown(
    id='dropdown',
    options=[
        {'label': i, 'value': i} for i in stations
    ],
    multi=False,
    value="Kamppi (M)"
)


def render_scatter(station, a, b):
    querry = "departure_name == '"+station+"'"
    y = list(hours.query(querry)['count'])
    x = list(range(24))
    x = x[a:b]
    y = y[a:b]
    fig = go.Figure(go.Bar(x=x, y=y, marker={'color': '#F09D51'}))
    #fig = go.Figure(go.Scatter(x=x,y=y,mode='lines+markers',name='lines+markers'))
    fig.update_layout(margin={"r": 0, "t": 20, "l": 0, "b": 35})
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[2, 6, 10, 14, 18, 22]
        )
    )
    fig.update_traces(hovertemplate='Hour: %{x}:00 - %{x}:59<br>No. departures: %{y}<extra></extra>')
    # fig.update_xaxes(visible=False)
    return fig


station_chart_slider = html.Div([
    dcc.RangeSlider(
        id='my-range-slider',
        min=0,
        max=24,
        step=1,
        value=[6, 20],
        #marks={i:f"{i}:00" for i in range(24)},
        marks={0: '0:00', 6: '6:00', 12: '12:00', 18: '18:00', 24: '24:00'}

    ),
    html.Div(id='output-container-range-slider')
])


@app.callback(
    Output('dropdown', 'value'),
    Output('hour_chart', 'figure'),
    Input('my-range-slider', 'value'),
    Input('dropdown', 'value')
)
def hour_graph(range, station):
    fig = render_scatter(station, range[0], range[1])
    return station, fig


stationslayout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Departures by station"),
            dropdown,
            dcc.Graph(figure=render_scatter(
                'Kamppi (M)', 6, 20), id='hour_chart'),
            station_chart_slider
        ], width=4),
        dbc.Col([
            html.H3("Helsinki stations map"),
            dcc.Graph(figure=mapa),
        ], width=8),
    ]),
])

data_tab = html.Div([
    dbc.Col([
        html.H3("Data Table"),
        table
    ], width=12),
])


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
        elif active_tab == "data_tab":
            return data_tab
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
    app.run_server(debug=False, port=8888)
