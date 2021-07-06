# Dashboard for Helsinki City Bikes

The project is focused on created meaningful dashboard for [dataset](https://www.kaggle.com/geometrein/helsinki-city-bikes) about usage of
shared bicycles available to the public in Helsinki and Espoo metropolitan areas for Data Visualization course on University Poznan of Technology.

The final result can be seen on this [website](https://helsinki-bikes.herokuapp.com/).

## Important note

Due to extensive size of the dataset, it is excluded from repository as it exceeds LFS free tier (2 GB) and thus the dataset needs to be
downloaded manually from the website (link for the dataset is included above).

## Content of dataset

Dataset consists of 14 attributes, some of them being:
- Names of stations
- Departure times
- Distance and time traveled
- Average speed in km/h


## Technology stack

The dashboard is created using:
- Python3
- Pandas
- [Flask](https://github.com/plotly/dash): framework for building web analytic applications
- [Plotly](https://github.com/plotly/plotly.py): interactive graphing library for Python
