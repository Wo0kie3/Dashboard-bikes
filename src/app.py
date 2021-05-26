# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import time
import dash
from dash_bootstrap_components._components.Container import Container
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

from dash.dependencies import Input, Output

stations = pd.read_csv("data/stations.csv")
stations = list(stations["Name"])

external_stylesheets = [dbc.themes.SKETCHY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#TABS

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Helsinki City Bikes Dashboard"),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label="Bikes", tab_id="bikes"),
                dbc.Tab(label="Stations", tab_id="stations"),
                dbc.Tab(label='About',tab_id='about'),
                dbc.Tab(label='Help',tab_id='help')
            ],
            id="tabs",
            active_tab="bikes",
        ),
        html.Br(),
        html.Div(id="tab-content", className="p-4"),
    ]
)
#style={'backgroundImage': 'url(/assets/BG.png)'}
bikeslayout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Test"),width=8),
                dbc.Col(html.Div("Test1"),width=4),
            ]
        ),
    ]
)

stationslayout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Temp"),width=6),
                dbc.Col(html.Div("Temp1"),width=3),
                dbc.Col(html.Div("Temp2"),width=3),
            ]
        ),
    ]
)

helplayout = html.Div()

aboutlayout = html.Div([
    html.H4("What are Helsinki City bikes?"),
    html.P("Helsinki City Bikes are shared bicycles available to the public in Helsinki and Espoo metropolitan areas. The main aim of the Helsinki city bike system is to address the so-called last-mile problem present in all distribution networks. The city bikes were introduced in 2016 as a pilot project with only 46 bike stations available in Helsinki. After becoming popular among the citizens, Helsinki city decided to gradually expand the bike network. In the period between 2017 and 2019, approximately one hundred stations were being added to the network each year. By 2019 the bike network reached its complete state with only 7 stations being added in 2020. As of 2020, there were 3,510 bikes and 350 stations operating in Helsinki and Espoo."),
    dbc.Alert("Since 2016 more than 10.000.000 rides have been made. The total distance of the trips is 25.291.523 kilometres. To put that in perspective 25.3 million kilometres is 65 times the distance to the moon. The total time all residents spent riding the bikes is approximately 280 Years and 4 months.", color="primary"),
    html.P("In order to use the city bikes, citizens purchase access for a day, week or the entire cycling season that lasts from April to November. All passes include an unlimited number of 30-minute bike rides. For an extra fee of 1€/hour, you can use the bike for longer. Bikes are picked up and returned to stations that are located all around Helsinki and Espoo."),
    html.H4("Dataset"),
    dcc.Link('Helsinki City Bikes on Kaggle.com',refresh=True, href='https://www.kaggle.com/geometrein/helsinki-city-bikes?fbclid=IwAR2v2jyT8aG1q1tEz61AGcezpBrm85zuiUV-d9uPgLY8Xr9Ly86JhEWNTg0'),

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