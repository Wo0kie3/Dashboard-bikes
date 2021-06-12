from datetime import datetime

import numpy as np
import pandas as pd

from config import (autumn_file, hourly_file, no_bins, reduced_file,
                    seasons_file, spring_file, stations_file, summer_file)


def _get_month_day(date_val: datetime):
    """
    Helper function for creating seasons dataset
    """
    return datetime(1970, date_val.month, date_val.day)


def get_all_seasons(data) -> list[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits data in three dataframes which are respectively:
    Spring, summer, autumn
    """
    seasons = data.drop(columns=[
        'return', 'departure_name', 'return_name',
        'departure_latitude', 'departure_longitude'
    ])

    seasons['departure'] = seasons['departure'] \
        .apply(lambda val: val.split()[0])

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

    return [spring, summer, autumn]


def create_seasons(data=None):
    """
    Creates (and returns) seasons dataset containing average values for all seasons.
    Excludes winter as the dataset does not contain data points in this period.
    """
    if data is None:
        data = pd.read_csv(reduced_file)

    spring, summer, autumn = get_all_seasons(data)

    season_names = ['spring', 'summer', 'autumn']
    columns = ['distance', 'duration', 'speed', 'temperature']

    seasons = pd.DataFrame(columns=columns)
    for _, season in enumerate([spring, summer, autumn]):
        values = [np.around(val, prec) for val, prec in zip(
            season.mean(numeric_only=True), [0, 0, 2, 2])]
        seasons = seasons.append(dict(zip(columns, values)), ignore_index=True)

    seasons.index = season_names

    seasons.to_csv(seasons_file)

    return seasons


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


def create_stations(data=None):
    """
    Creates (and returns) stations dataset containing name, coordinates, 
    count of departures and traffic of all stations.
    """
    if data is None:
        data = pd.read_csv(reduced_file)

    stations = data.groupby(by=[
        'departure_name', 'departure_latitude', 'departure_longitude'
    ]).size()                           \
        .sort_values(ascending=False)   \
        .reset_index()                  \
        .rename(columns={0: 'count'})   \

    stations = stations.reset_index().rename(columns={0: 'count'})
    stations['traffic'] = categorize(stations['count'])

    stations.to_csv(stations_file, index=False)

    return stations


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


def _assign_bins(values: pd.Series, no_bins, column_names) -> pd.DataFrame:
    """
    Assigns values to bins [1; no_bins]
    :return: DataFrame with three columns: bin, left_bound, right_bound
    """
    limits = np.linspace(values.min(), values.max(), no_bins)
    return pd.DataFrame(
        np.array([_find_bin(limits, val) for val in values.values]),
        columns=column_names
    )


def get_bins(no_bins, data=None):
    """
    Creates bins for given data
    """
    if data is None:
        data = pd.read_csv(reduced_file)

    columns_names = ["bin", "left_bound", "right_bound"]
    bins = _assign_bins(data['distance'], no_bins, columns_names)

    bins['bin'] = pd.to_numeric(bins['bin'])
    bins['interval'] = " " + bins["left_bound"] + \
        " - " + bins["right_bound"]

    return bins


def _get_distances(df, groupby_cols: list, sortby: list, rename_cols: dict):
    """
    Groups dataframe by groupby_cols param and returns
    sorted (by sortby) dataframe
    """
    return df.groupby(by=groupby_cols)   \
        .count()                    \
        .reset_index()              \
        .sort_values(by=sortby)     \
        .rename(columns=rename_cols)


def create_distances(no_bins, data=None) -> list[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Creates (and returns) distances dataset needed for rose plot
    """
    if data is None:
        data = pd.read_csv(reduced_file)

    spring, summer, autumn = get_all_seasons(data)

    spring_bins = get_bins(no_bins, spring)
    summer_bins = get_bins(no_bins, summer)
    autumn_bins = get_bins(no_bins, autumn)

    groupby_cols = ['bin', 'left_bound', 'interval']
    sortby = ['bin']
    rename_cols = {'right_bound': 'count'}

    spring = _get_distances(spring_bins, groupby_cols, sortby, rename_cols)
    summer = _get_distances(summer_bins, groupby_cols, sortby, rename_cols)
    autumn = _get_distances(autumn_bins, groupby_cols, sortby, rename_cols)

    spring.to_csv(spring_file)
    summer.to_csv(summer_file)
    autumn.to_csv(autumn_file)

    return [spring, summer, autumn]


def _get_hour(date_val: datetime):
    """
    Returns rounded hour from the datetime
    """
    hour, minute = date_val.hour, date_val.minute
    if minute >= 30:
        hour += 1
        if hour == 24:
            hour = 0

    return hour


def create_hourly(data=None) -> pd.DataFrame:
    """
    Creates (and returns) dataset containing hourly data for each station
    """
    if data is None:
        data = pd.read_csv(reduced_file)

    hourly = data.drop(columns=[
        'return', 'return_name', 'departure_latitude', 'departure_longitude'
    ])

    hourly = hourly.astype({'departure': 'datetime64'})
    hourly['departure'] = hourly['departure'].apply(_get_hour)

    hourly = data.groupby(by=['departure_name', 'departure']) \
        .size()                                       \
        .reset_index()                                \
        .rename(columns={'departure': 'hour', 0: 'count'})

    hourly.to_csv(hourly_file)

    return hourly


if __name__ == '__main__':
    reduced = pd.read_csv(reduced_file)
    reduced['departure'] = reduced['departure'].apply(
        lambda val: val.split()[0]
    )

    create_distances(no_bins, reduced)
    create_seasons(reduced)
    create_stations(reduced)
    create_hourly(reduced)
