from os.path import dirname, realpath


class Season:
    SPRING = 'spring'
    SUMMER = 'summer'
    AUTUMN = 'autumn'


class Color:
    GREEN = '#99c945'
    RED = '#ff7771'
    YELLOW = '#fecb52'


# Retrieve realpath of running script and get only dir name
data_dir = dirname(realpath(__file__)) + '/../data/'

# Files
reduced_file = data_dir + "reduced.csv"
stations_file = data_dir + "stations.csv"
hourly_file = data_dir + "hourly_stations.csv"
seasons_file = data_dir + "seasons.csv"

spring_file = data_dir + "spring_distances.csv"
summer_file = data_dir + "summer_distances.csv"
autumn_file = data_dir + "autumn_distances.csv"

paragraph_1 = data_dir + "paragraph1help.txt"
paragraph_2 = data_dir + "paragraph2help.txt"
alert_help = data_dir + "alerthelp.txt"

# Token
mapbox_token = data_dir + ".mapbox_token"

# Number of bins for rose plot
no_bins = 20

# Attributes for scatter plot
left_bound = 6
right_bound = 20
