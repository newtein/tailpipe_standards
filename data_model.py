from collections import OrderedDict
import numpy as np
import pandas as pd
import os
from constants import *
import logging
from get_population import USPopulation
from copy import deepcopy


class DataModel:
    def __init__(self, config):
        self.config = config
        self.data = self.init_data()
        self.population_obj = USPopulation()

    def init_data(self):
        data = OrderedDict()
        start_year, end_year = self.config.get_start_end_years(self.config.working_db)
        for year in range(start_year, end_year+1):
            if year not in data:
                data[year] = OrderedDict()
            for month in range(1, 13):
                data[year][month] = {i:np.nan for i in self.config.pollutant_list}
        return data

    def populate_dataframe(self, data):
        columns = self.config.get_column_names()
        list_of_dicts = []
        for year in data:
            for month in data[year]:
                temp = {
                        "year": year,
                        "month": month
                    }
                temp.update(data[year][month])
                list_of_dicts.append(temp)
        df = pd.DataFrame(columns = columns, data = list_of_dicts)
        return df

    def update_to_df(self, emission_results):
        data = self.init_data()
        for pollutant in emission_results:
            for emission_info in emission_results[pollutant]:
                year, month = emission_info.get("yearID"), emission_info.get("monthID")
                emission = emission_info.get('emission')
                data[year][month][pollutant] = emission
        df = self.populate_dataframe(data)
        return df

    def combine_dfs(self, dfs):
        county_dfs = {}
        for index, geo_info in enumerate(zip(self.config.county, self.config.state)):
            county, state = geo_info[0], geo_info[1]
            df_key = get_df_key(county, state)
            db_info = self.config.db[index]
            if type(db_info) == list:
                combined_county_df = pd.DataFrame()
                for db in db_info:
                    # print("combining {} / {}".format(db, db_info))
                    combined_county_df = combined_county_df.append(dfs.get(db))
                county_dfs[df_key] = combined_county_df
                #print(combined_county_df[combined_county_df['year'] == 1999])
            else:
                county_dfs[df_key] = dfs.get(db_info)
        for county in county_dfs:
            df = county_dfs.get(county)
            w_filename = os.path.join(OUTPUT_TABLE_DIR, self.config.get_filename(c=county))
            df.to_csv(w_filename, index=False)
            logging.info("File {} written.".format(w_filename))
        return county_dfs

    def adjust_population(self, _df_wrapper):
        adjusted_df_wrapper = {}
        df_wrapper = deepcopy(_df_wrapper)
        for geo_info in df_wrapper:
            county_name, state_name = split_df_key(geo_info)
            county_index = self.config.county.index(county_name)
            state_name = self.config.state[county_index]
            population_lookup = self.population_obj.get(county_name, state_name)
            df = df_wrapper.get(geo_info)
            for pollutant in self.config.pollutant_list:
                t = []
                for index, row in df.iterrows():
                    year = row['year']
                    population = population_lookup.get(year)
                    emission = row[pollutant]
                    try:
                        population_adjusted_emission = (emission*1000)/population
                    except:
                        print(year, population, county_name, state_name, emission, population_lookup)
                    t.append(population_adjusted_emission)
                df[pollutant] = t
            adjusted_df_wrapper[county_name] = df
        return adjusted_df_wrapper




