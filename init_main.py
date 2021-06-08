import os
import sys
from local_logger import LocalLogger
from constants import *
from pollutantClass import Pollutant
from EmissionsClass import EmissionClass
from config_reader import ConfigReader
from data_model import DataModel
from emission_plot import EmissionPlot
from county_plot import CountyPlot
import pandas as pd

logging = LocalLogger().setup()


def get_pollutants_df():
    dfs = {}
    data_obj = DataModel(config)
    for db_info in config.unwrap_dbs():
        db_index, db = db_info[0], db_info[1]
        county_name = config.county[db_index]
        logging.info("Executing for db {}.".format(db))
        config.working_db = db
        emission_class_obj = EmissionClass(config.working_db, county_name)
        emission_results = {}
        for pollutant in config.pollutant_list:
            pollutant_id = pollutant_obj.get_id_from_shortname(pollutant)
            logging.info("[{}] Executing for pollutant {}/{}.".format(db, pollutant_id, pollutant))
            start_year, end_year = config.get_start_end_years(db)
            emission_result = emission_class_obj.calculate_emission_by_pollutant_monthly(start_year,
                                                                                         end_year, pollutant_id,
                                                                                         pollutant)
            emission_results[pollutant] = emission_result
        df = data_obj.update_to_df(emission_results)
        logging.info('Analysis on database {} completed.'.format(config.working_db))
        dfs[db] = df
    dfs = data_obj.combine_dfs(dfs)
    population_adjusted_wrapper = None
    if config.population_adjusted:
        population_adjusted_wrapper = data_obj.adjust_population(dfs)
    return dfs, population_adjusted_wrapper


def plot_graphs(_df_wrapper, title=None):
    eplot_obj = EmissionPlot(config, _df_wrapper, title=title)
    eplot_obj.plot_pollutants()
    cplot_obj = CountyPlot(config, _df_wrapper, title=title)
    cplot_obj.plot_counties()


if __name__ == "__main__":
    try:
        sys.argv[1] and sys.argv[1] in os.listdir(INPUT_DIR)
    except:
        logging.error("Please supply the configuration filename. Note: Configuration file should be present in "
                      "input_configs")
    finally:
        input_config_path = os.path.join(INPUT_DIR, sys.argv[1])
        config = ConfigReader(input_config_path)
        pollutant_obj = Pollutant()
        logging.info(pollutant_obj.sanitize(config.pollutant_list))
        df_wrapper, population_adjusted_df_wrapper = get_pollutants_df()
        plot_graphs(df_wrapper, title=config.figure_title)
        if config.population_adjusted:
            plot_graphs(population_adjusted_df_wrapper, title=config.figure_title+" per 1000 people")




