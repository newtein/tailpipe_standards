
INPUT_DIR = "input_configs"
OUTPUT_TABLE_DIR = "output_tables"
OUTPUT_FIG_DIR = "output_images"
US_CENSUS_DIR = "us_census"
CENSUS_DATA_PATH = US_CENSUS_DIR+"/2010_2019_population.csv"
AMBIENT_AIR_DATA = "ambient_air_data"


def get_df_key(county, state):
    return "{}${}".format(county.replace(" ", "_"), state.replace(" ", "_"))


def split_df_key(key):
    county_name, state_name = key.split('$')
    return county_name.replace("_", " "), state_name.replace("_", " ")
