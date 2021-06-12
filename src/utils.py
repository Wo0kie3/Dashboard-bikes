from pathlib import Path
from datasets import create_stations, create_seasons, create_hourly
from config import stations_file, seasons_file, hourly_file


def file_exists(file_path: str):
    if Path(file_path).is_file():
        return True

    return False


def create_datasets():
    if not file_exists(stations_file):
        create_stations()

    if not file_exists(seasons_file):
        create_seasons()

    if not file_exists(hourly_file):
        create_hourly()
