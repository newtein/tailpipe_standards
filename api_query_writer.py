from query_data import QueryEPAData
import pandas as pd
import json
import time
from constants import *
import os
import logging


class APIQUERYWriter:
    def __init__(self, config):
        self.config = config
        self.key = self.get_epa_key()
        self.path = AMBIENT_AIR_DATA
        self.state_codes, self.county_codes = self.get_state_county_codes()
        self.plot_distribution = self.config.plot_distribution
        self.plot_distribution = "daily" if self.plot_distribution in ["daily", "monthly"] else self.plot_distribution

    def get_epa_key(self):
        with open("D:/epa_key.txt", "r") as f:
            key = f.readline().strip()
        return key

    def get_filename(self, parameter, state_code, start_year, end_year, county_code=None):
        if county_code:
            fname = "{}/{}_{}_{}_{}_{}_{}.csv".format(self.path, self.plot_distribution, parameter, start_year, end_year, state_code, county_code)
        else:
            fname = "{}/{}_{}_{}_{}_{}.csv".format(self.path, self.plot_distribution, parameter, start_year, end_year, state_code)
        return fname

    def get_state_county_codes(self):
        df = pd.read_csv('states_and_counties.csv', dtype=str)
        state_codes, county_codes = [], []
        for state, county in zip(self.config.state, self.config.county):
            t_county = county.replace("County", "").strip()
            f1 = (df['State Name'] == state)
            f2 = (df['County Name'] == t_county)
            t_df = df[f1 & f2]
            scode = t_df['State Code'].tolist()[0]
            ccode = t_df['County Code'].tolist()[0]
            state_codes.append(scode)
            county_codes.append(ccode)
        return state_codes, county_codes

    def get_data(self, parameter, start_year, end_year, refresh=False):
        dfs = {}
        for state_code, county_code in zip(self.state_codes, self.county_codes):
            index = self.county_codes.index(county_code)
            county_name, state_name = self.config.county[index], self.config.state[index]
            # dict_key = "{}_{}".format(state_code, county_code)
            df_key = get_df_key(county_name, state_name)
            filename = self.get_filename(parameter, state_code, start_year, end_year, county_code=county_code)
            if os.path.exists(filename) and not refresh:
                df = pd.read_csv(filename, dtype={'state_code': str, 'county_code': str, 'site_number': str})
            else:
                df = self.write_data(parameter, state_code, start_year, end_year, filename, county_code=county_code)
            dfs[df_key] = df
        return dfs

    def write_data(self, parameter, state_code, start_year, end_year, fname, county_code=None):
        date_combinations = self.get_epa_start_end_year_combo(start_year, end_year)
        df = pd.DataFrame()
        for date in date_combinations:
            sdate, edate = date[0], date[1]
            dict_data = QueryEPAData(self.key, parameter, state_code, sdate, edate, county_code=county_code,
                                     plot_distribution=self.plot_distribution).hit()
            data = dict_data.get("Data")
            if not data:
                logging.info("Failed to fetch data: {}".format(dict_data))
            json_data = json.dumps(data)
            t = pd.read_json(json_data, dtype={'state_code': str, 'county_code': str, 'site_number':str})
            df = df.append(t)
            logging.info("API request completed for state/county: {}/{} | {} - {}".format(state_code, county_code,
                                                                                          sdate, edate))
            time.sleep(6)
        df.to_csv(fname, index=False)
        return df

    def get_key(self, x):
        return " ".join([i.capitalize() for i in x.split('_')])

    def get_epa_start_end_year_combo(self, start_year, end_year):
        combos = []
        for year in range(start_year, end_year+1):
            sdate = "{}{}{}".format(year, "01", "01")
            edate = "{}{}{}".format(year, "12", "31")
            combos.append((sdate, edate))
        return combos


if __name__=="__main__":
        """
        # PM10 Ozone NO2 SO2 CO
        parameters = ["81102", "44201", "42602", "42401", "42101"]
        """
        parameters = ["81102", "44201", "42602", "42401", "42101"]
        for p in parameters:
            query_obj = APIQUERYWriter()
            query_obj.write_data(p)
            # query_obj.join_files(p)