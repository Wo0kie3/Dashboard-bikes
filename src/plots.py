from os.path import dirname, realpath

import numpy as np
import pandas as pd
import plotly.express as px

# Retrieve realpath of running script and get only dir name
data_dir = dirname(realpath(__file__)) + '/../data/'
# Number of bins for rose plot
no_bins = 20


def _find_bin(limits, val):
    """
    Helping function for assign_bins implementing binary search
    :return: [bin_no, left_bound, right_bound]
    """
    left, right = 0, len(limits) - 1
    lefts, rights, mids = [left], [right], []
    while left <= right:
        mid = left + (right - left) // 2
        mids.append(mid)

        if right - left == 0:
            # Return bin and interval
            if val < limits[mid]:
                return [mid, str(limits[mid - 1]), str(limits[mid])]
            else:
                right_interval = "inf" if (mid + 1) == len(limits) else str(limits[mid + 1])
                return [mid + 1, str(limits[mid]), right_interval]

        if val == limits[mid]:
            # Return left bin
            return [mid, str(limits[mid - 1]), str(limits[mid])]

        if val < limits[mid]:
            # Get left half
            right = mid - 1
            lefts.append(-1)
            rights.append(right)
        else:
            # Get right half
            left = mid + 1
            lefts.append(left)
            rights.append(-1)

    return [mid, str(limits[mid - 1]), str(limits[mid])]


def assign_bins(values: pd.Series, no_bins, column_names) -> pd.DataFrame:
    """
    Assigns values to bins [1; no_bins]
    """
    limits = np.linspace(values.min(), values.max(), no_bins)
    return pd.DataFrame(
        np.array([_find_bin(limits, val) for val in values.values]),
        columns=column_names
    )


def plot_rose(df: pd.DataFrame, r, theta, hover_data={}, labels={}, title='') -> None:
    # TODO: Add docstring
    fig = px.bar_polar(
        df, r='count', theta='left_bound', labels=labels, 
        title=title, start_angle=0, template='ggplot2',
        hover_data={}, 
        direction='counterclockwise'
    )

    fig.show()


if __name__ == '__main__':
    df = pd.read_csv(data_dir + 'reduced.csv')

    columns_names = ["bin", "left_bound", "right_bound"]
    bins = assign_bins(df['distance'], no_bins, columns_names)

    bins['bin'] = pd.to_numeric(bins['bin'])
    bins['interval'] = " " + bins["left_bound"] + " - " + bins["right_bound"]

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

    plot_rose(distances, 'count', 'left_bound', hover_data, labels, title)

