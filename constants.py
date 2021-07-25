
INPUT_DIR = "input_configs"
OUTPUT_TABLE_DIR = "output_tables"
OUTPUT_FIG_DIR = "output_images"
US_CENSUS_DIR = "us_census"
CENSUS_DATA_PATH = US_CENSUS_DIR+"/2010_2019_population.csv"
AMBIENT_AIR_DATA = "ambient_air_data"
CARB = [6, 41, 53, 9,10, 23, 24,25, 34, 36,42,44, 50, 11]


def get_df_key(county, state):
    return "{}${}".format(county.replace(" ", "_"), state.replace(" ", "_"))


def split_df_key(key):
    county_name, state_name = key.split('$')
    return county_name.replace("_", " "), state_name.replace("_", " ")
