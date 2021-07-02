from combine_multiple_pollutants import CombineMultiplePollutants
from api_query_writer import APIQUERYWriter
import logging
from constants import *


class AmbientAirDf:
    def __init__(self, config):
        self.config = config

    def get_ambient_pollution_df(self):
        dfs = {}
        epa_query_obj = APIQUERYWriter(self.config)
        state_codes, county_codes = epa_query_obj.state_codes, epa_query_obj.county_codes
        for index, epa_pollutant_code in enumerate(self.config.epa_pollutant_code):
            pollutant = self.config.pollutant_list[index]
            logging.info("[Ambient air] Begin for EPA Pollutant Code {}".format(epa_pollutant_code))
            epa_df_wrapper = epa_query_obj.get_data(epa_pollutant_code, self.config.start_year, self.config.end_year)
            dfs[pollutant] = epa_df_wrapper
            logging.info("[Ambient air] Completed for EPA Pollutant Code {}".format(epa_pollutant_code))
        dfs = {}
        year = "{}_{}".format(self.config.start_year, self.config.end_year)
        for state_code, county_code in zip(state_codes, county_codes):
            index = county_codes.index(county_code)
            state_name, county_name = self.config.state[index], self.config.county[index]
            county_identifier = "{}_{}".format(state_code, county_code)
            combined_pol_obj = CombineMultiplePollutants(self.config.epa_pollutant_code, year, county_identifier=county_identifier)
            dict_key = get_df_key(county_name, state_name)
            dfs[dict_key] = combined_pol_obj.combine_pollutants()
        return dfs

    def standardized_ambient_df(self, dfs):
        new_dfs = {}
        for key in dfs:
            ambient_df = dfs.get(key)
            ambient_df['year'] = ambient_df['date'].apply(lambda x: x.year)
            ambient_df['month'] = ambient_df['date'].apply(lambda x: x.month)
            for epa_code, pollutant_name in zip(self.config.epa_pollutant_code, self.config.pollutant_list):
                ambient_df[pollutant_name] = ambient_df[epa_code]
            df = ambient_df.groupby(['year', 'month'])[self.config.pollutant_list].apply(sum).reset_index()
            new_dfs[key] = df
        return new_dfs