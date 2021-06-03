from pathlib import Path


def file_exists(file_path: str):
    if Path(file_path).is_file():
        return True

    return False