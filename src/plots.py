import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.missing_ipywidgets import FigureWidget

from config import (Color, Season, autumn_file, mapbox_token, no_bins,
                    spring_file, stations_file, summer_file, hourly_file)
from datasets import create_distances
from utils import file_exists


def plot_rose(df: pd.DataFrame, r, theta, hover_data={},
              labels={}, color=Color.RED) -> FigureWidget:
    """
    Draws rose plot figure and returns it
    """
    fig = px.bar_polar(
        df, r=r, theta=theta, labels=labels,
        start_angle=0, template='ggplot2',
        hover_data=hover_data, direction='counterclockwise',
        color_discrete_sequence=[color]
    )

    return fig


def get_rose_plot(no_bins=no_bins, season='spring') -> FigureWidget:
    """
    Returns rose plot figure for chosen season
    """
    if not file_exists(spring_file):
        create_distances(no_bins)

    if season == Season.SPRING:
        dist_file = spring_file
        color = Color.GREEN
    elif season == Season.SUMMER:
        dist_file = summer_file
        color = Color.RED
    elif season == Season.AUTUMN:
        dist_file = autumn_file
        color = Color.YELLOW
    else:
        raise Exception(
            "season must have value equal to one of the following: " +
            "spring, summer, autumn"
        )

    distances = pd.read_csv(dist_file)
    distances['left_bound'] = distances['left_bound'].astype(str)

    hover_data = {
        'interval': True,
        'left_bound': False,
        'bin': False
    }
    labels = {
        'count': 'No. people',
        'interval': 'Distance interval '
    }

    return plot_rose(
        distances, 'count', 'left_bound', hover_data, labels, color
    )


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
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    return fig


def get_mapbox_plot() -> FigureWidget:
    """
    Returns rose plot figure for chosen season
    """
    stations = pd.read_csv(stations_file)

    stations.replace({'traffic': {
        'very high': 'Very high',
        'high': 'High',
        'moderate': 'Moderate',
        'low': 'Low',
        'very low': 'Very low'
    }}, inplace=True)

    labels = {'traffic': "Traffic:"}

    return plot_mapbox(
        df=stations, lat='departure_latitude', lon='departure_longitude',
        text='departure_name', center=[60.19525, 24.9013], size='count',
        color='traffic', labels=labels
    )


def get_scatter_plot(station, left, right, hours=None):
    """
    Returns scatter plot for chosen station
    """
    if hours is None:
        hours = pd.read_csv(hourly_file)

    count = list(hours.query("departure_name == '"+station+"'")['count'])[left:right]
    hour_range = list(range(24))[left:right]

    fig = go.Figure(go.Bar(x=hour_range, y=count, marker={'color': '#F09D51'}))

    fig.update_layout(
        margin={"r": 0, "t": 20, "l": 0, "b": 35},
        xaxis=dict(
            tickmode='array',
            tickvals=[2, 6, 10, 14, 18, 22]
        )
    )

    fig.update_traces(
        hovertemplate='Period: %{x}:00 - %{x}:59<br>No. departures: %{y}<extra></extra>')

    return fig


if __name__ == '__main__':
    rose = get_rose_plot(no_bins, Season.SPRING)
    rose.show()
    rose = get_rose_plot(no_bins, Season.SUMMER)
    rose.show()
    rose = get_rose_plot(no_bins, Season.AUTUMN)
    rose.show()

    mapbox = get_mapbox_plot()
    mapbox.show()

    scatter = get_scatter_plot()
