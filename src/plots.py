from os.path import dirname, realpath

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.missing_ipywidgets import FigureWidget
from datasets import create_bins

from utils import file_exists

# Retrieve realpath of running script and get only dir name
data_dir = dirname(realpath(__file__)) + '/../data/'

# Files
bin_file = data_dir + "bins.csv"
station_file = data_dir + "stations.csv"
seasons_file = data_dir + "seasons.csv"
mapbox_token = data_dir + ".mapbox_token"

# Number of bins for rose plot
no_bins = 20


def plot_rose(df: pd.DataFrame, r, theta, hover_data={}, labels={}, title='') -> FigureWidget:
    """
    Draws rose plot figure and returns it
    """
    fig = px.bar_polar(
        df, r=r, theta=theta, labels=labels,
        title=title, start_angle=0, template='ggplot2',
        hover_data=hover_data,
        direction='counterclockwise'
    )

    return fig


def plot_mapbox(df: pd.DataFrame, lat, lon, text, center: list, size=None, color=None, labels={}) -> FigureWidget:
    """
    Draws mapbox plot figure and returns it
    """
    fig = px.scatter_mapbox(
        df, lat=lat, lon=lon, size=size, color=color, text=text, zoom=10,
        template='plotly', mapbox_style='basic', labels=labels
    )

    fig.update_traces(
        hovertemplate="(%{lat}, %{lon})<br>%{text}<extra></extra>"
    )

    c_lat, c_lon = center

    fig.update_layout(
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=c_lat,
                lon=c_lon
            )
        ),
        margin={'r': 5, 'l': 5, 't': 30, 'b': 5}
    )

    return fig


def get_rose_plot():
    if file_exists(bin_file):
        bins = pd.read_csv(bin_file)
        bins['left_bound'] = bins['left_bound'].astype(str)
    else:
        create_bins(pd.read_csv(data_dir + 'reduced.csv'), no_bins)

    distances = bins.groupby(by=['bin', 'left_bound', 'interval']) \
        .count()                                                   \
        .reset_index()                                             \
        .sort_values(by=['bin'])                                   \
        .rename(columns={'right_bound': 'count'})

    hover_data = {
        'interval': True,
        'left_bound': False,
        'bin': False
    }
    labels = {
        'count': 'No. people',
        'interval': 'Distance interval '
    }
    title = 'Distance plot, something...'

    return plot_rose(distances, 'count', 'left_bound', hover_data, labels, title)


def get_mapbox_plot():
    stations = pd.read_csv(data_dir + 'stations.csv')

    stations.replace({'traffic': {
        'very high': 'Very high',
        'high': 'High',
        'moderate': 'Moderate',
        'low': 'Low',
        'very low': 'Very low'
    }}, inplace=True)

    px.set_mapbox_access_token(open(mapbox_token).read())

    labels = {'traffic': "Traffic:"}

    return plot_mapbox(
        df=stations, lat='departure_latitude', lon='departure_longitude',
        text='departure_name', center=[60.19525, 24.9013], size='count',
        color='traffic', labels=labels
    )


if __name__ == '__main__':
    rose = get_rose_plot()
    rose.show()

    mapbox = get_mapbox_plot()
    mapbox.show()
