from os.path import dirname, realpath

import numpy as np
import pandas as pd
import plotly.express as px

# Retrieve realpath of running script and get only dir name
data_dir = dirname(realpath(__file__)) + '/../data/'

# Number of bins for rose plot
no_bins = 16


def _find_bin(limits, val):
    """
    Helping function for assign_bins implementing binary search
    """
    left, right = 0, len(limits) - 1
    while left <= right:
        mid = left + (right - left) // 2

        if right - left == 0:
            if val < limits[mid]:
                # print(f'{val} assiging to bin no.{mid}')
                return mid
            else:
                # print(f'{val} assiging to bin no.{mid + 1}')
                return mid + 1

        if val == limits[mid]:
            # Return left bin
            # print(f'{val} assiging to bin no.{mid}')
            return mid

        if val < limits[mid]:
            # Get left half
            right = mid - 1
        else:
            # Get right half
            left = mid + 1


def assign_bins(values: pd.Series, no_bins) -> pd.DataFrame:
    """
    Assigns values to bins [1; no_bins]
    """
    limits = np.linspace(values.min(), values.max(), no_bins)
    return values.apply(lambda val: _find_bin(limits, val))


def plot_rose(df: pd.DataFrame) -> None:
    fig = px.bar_polar(
        df, r='count', theta='bin'
    )

    fig.show()


if __name__ == '__main__':
    df = pd.read_csv(data_dir + 'reduced.csv')

    bins = assign_bins(df['distance'], no_bins)
    distances = pd.DataFrame({
        'distance': df['distance'],
        'bin': (360 / no_bins) * bins
    })
    distances = distances.groupby(by='bin') \
        .count()                            \
        .reset_index()                      \
        .rename(columns={'distance': 'count'})

    plot_rose(distances)

