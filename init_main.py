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
from correlation_plot import CorrelationPlot
from county_boxplot import CountyBoxplot
from bar_plot import BarPlot
from get_ambient_air_pollution_df import AmbientAirDf
from efficacy_calculator import Efficacy
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
        emission_class_obj = EmissionClass(config, county_name)
        emission_results = {}
        for pollutant in config.pollutant_list:
            pollutant_id = pollutant_obj.get_id_from_shortname(pollutant)
            logging.info("[{}] Executing for pollutant {}/{}.".format(db, pollutant_id, pollutant))
            start_year, end_year = config.get_start_end_years(db)
            emission_result = emission_class_obj.get_emission(start_year,end_year, pollutant_id,pollutant)
            emission_results[pollutant] = emission_result
        df = data_obj.update_to_df(emission_results)
        logging.info('Analysis on database {} completed.'.format(config.working_db))
        dfs[db] = df
    dfs = data_obj.combine_dfs(dfs)
    # population_adjusted_wrapper = None
    # if config.population_adjusted:
    #     population_adjusted_wrapper = data_obj.adjust_population(dfs)
    # return dfs, population_adjusted_wrapper
    return dfs


def adjust_and_plot(_df_wrapper, _title=None, _pollutant_units=None):
    data_obj = DataModel(config)
    if config.plots:
        plot_graphs(_df_wrapper, _title=_title, _pollutant_units=_pollutant_units)
    if config.population_adjusted:
        population_adjusted_wrapper = data_obj.adjust_population(_df_wrapper)
        if config.plots:
            plot_graphs(population_adjusted_wrapper, _title=_title+" per 1000 people", _pollutant_units=_pollutant_units)


def plot_graphs(_df_wrapper, _title=None, _pollutant_units=None):
    eplot_obj = EmissionPlot(config, _df_wrapper, title=_title)
    eplot_obj.plot_pollutants()
    cplot_obj = CountyPlot(config, _df_wrapper, title=_title, pollutant_units=_pollutant_units)
    cplot_obj.plot_counties()
    if config.boxplot:
        cbplt_obj = CountyBoxplot(config, _df_wrapper, title=_title)
        cbplt_obj.plot_counties()
    if config.correlation and "per 1000 people" not in _title:
        corrplt_obj = CorrelationPlot(config, _df_wrapper, title=_title)
        corrplt_obj.plot_counties()


if __name__ == "__main__":
    try:
        sys.argv[1] and sys.argv[1] in os.listdir(INPUT_DIR)
    except:
        logging.error("Please supply the configuration filename. Note: Configuration file should be present in "
                      "input_configs")
    finally:
        # input_config_path = os.path.join(INPUT_DIR, sys.argv[1])
        input_config_path = sys.argv[1]
        config = ConfigReader(input_config_path)
        pollutant_obj = Pollutant()
        logging.info(pollutant_obj.sanitize(config.pollutant_list))
        # Ambient
        if config.ambient:
            ambient_obj = AmbientAirDf(config)
            ambient_df_wrapper = ambient_obj.get_ambient_pollution_df()
            ambient_df_wrapper = ambient_obj.standardized_ambient_df(ambient_df_wrapper)
            title = config.figure_title + " — Ambient Air"
            pollutant_units = ambient_obj.get_pollutant_units()
            adjust_and_plot(ambient_df_wrapper, _title=title, _pollutant_units=pollutant_units)
        # MOVES
        if config.onroad:
            df_wrapper = get_pollutants_df()
            title = config.figure_title + " — Onroad Emission"
            adjust_and_plot(df_wrapper, _title=title)
        # Efficacy
        if config.ambient and config.onroad and config.efficacy:
            efficacy_wrapper = {}
            for county, state in zip(config.county, config.state):
                key = get_df_key(county, state)
                ambient_df = ambient_df_wrapper.get(key)
                onroad_df = df_wrapper.get(key)
                efficacy_obj = Efficacy(config, ambient_df, onroad_df)
                columns = ["start_year", "end_year", "pollutant", "contribution", "efficacy"]
                t_append = []
                for pollutant in config.pollutant_list:
                    report = efficacy_obj.get_efficacy(config.start_year, config.end_year, pollutant)
                    t_append.append(report)
                efficacy_df = pd.DataFrame(columns=columns, data=t_append)
                efficacy_wrapper[key] = efficacy_df
            data_obj = DataModel(config)
            efficacy_wrapper = data_obj.merge_counties(efficacy_wrapper)
            bar_obj = BarPlot(config, efficacy_wrapper, title="Efficacy")
            bar_obj.plot_counties()
            # print(efficacy_wrapper)



