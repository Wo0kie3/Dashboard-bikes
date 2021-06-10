from datetime import datetime

import numpy as np
import pandas as pd

from plots import data_dir


def _get_month_day(date_val: datetime):
    """
    Helper function for creating seasons dataset
    """
    return datetime(1970, date_val.month, date_val.day)


def create_seasons(data):
    """
    Creates seasons dataset containing average values for all seasons.
    Excludes winter as the dataset does not contain data points in this period.
    """
    seasons = data.drop(columns=[
        'return', 'departure_name', 'return_name',
        'departure_latitude', 'departure_longitude'
    ])

    seasons = seasons.astype({'departure': 'datetime64'})

    spring = seasons.iloc[seasons['departure'].apply(_get_month_day)
                          .to_frame()
                          .query('19700320 <= departure < 19700621').index, :]

    summer = seasons.iloc[seasons['departure'].apply(_get_month_day)
                          .to_frame()
                          .query('19700621 <= departure < 19700922').index, :]

    autumn = seasons.iloc[seasons['departure'].apply(_get_month_day)
                          .to_frame()
                          .query('19700922 <= departure < 19701222').index, :]

    season_names = ['spring', 'summer', 'autumn']
    columns = ['distance', 'duration', 'speed', 'temperature']

    seasons = pd.DataFrame(columns=columns)
    for _, season in enumerate([spring, summer, autumn]):
        values = [np.around(val, prec) for val, prec in zip(
            season.mean(numeric_only=True), [0, 0, 2, 2])]
        seasons = seasons.append(dict(zip(columns, values)), ignore_index=True)

    seasons.index = season_names

    seasons.to_csv(data_dir + 'seasons.csv')


def _get_category(val, quants: pd.Series):
    """
    Helper function for categorize
    """
    names = ['very low', 'low', 'moderate', 'high', 'very high']
    for ind, quant in enumerate(quants):
        if val <= quant:
            return names[ind]

    return names[-1]


def categorize(vals: pd.Series) -> pd.Series:
    """
    Categorizes data based on their traffic (count of departures)
    """
    quants = vals.quantile([0.2, 0.4, 0.6, 0.8])
    return vals.apply(lambda val: _get_category(val, quants))


def create_stations(data):
    """
    Creates stations dataset containing name, coordinates, count of departures
    and traffic of all stations.
    """
    stations = data.groupby(by=[
        'departure_name', 'departure_latitude', 'departure_longitude'
    ]).size()                           \
        .sort_values(ascending=False)   \
        .reset_index()                  \
        .rename(columns={0: 'count'})   \

    stations = stations.reset_index().rename(columns={0: 'count'})
    stations['traffic'] = categorize(stations['count'])

    stations.to_csv(data_dir + 'stations.csv', index=False)


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
                right_interval = "inf" if (
                    mid + 1) == len(limits) else str(limits[mid + 1])
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
    :return: DataFrame with three columns: bin, left_bound, right_bound
    """
    limits = np.linspace(values.min(), values.max(), no_bins)
    return pd.DataFrame(
        np.array([_find_bin(limits, val) for val in values.values]),
        columns=column_names
    )


def create_bins(data, no_bins):
    """
    Creates bins dataset needed for rose plot
    """
    columns_names = ["bin", "left_bound", "right_bound"]
    bins = assign_bins(data['distance'], no_bins, columns_names)

    bins['bin'] = pd.to_numeric(bins['bin'])
    bins['interval'] = " " + bins["left_bound"] + \
        " - " + bins["right_bound"]

    bins.to_csv(data_dir + 'bins.csv', index=False)


if __name__ == '__main__':
    reduced = pd.read_csv(data_dir + 'reduced.csv')
    reduced['departure'] = reduced['departure'].apply(
        lambda val: val.split()[0]
    )

    create_bins(reduced)
    create_seasons(reduced)
    create_stations(reduced)
