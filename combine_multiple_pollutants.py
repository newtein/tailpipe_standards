from read_data import ReadData
import pandas as pd
from constants import *


class CombineMultiplePollutants:
    def __init__(self, pollutants, year, state_code=None, filter_city_list=[], lag=None, county_identifier=None,
                 plot_distribution='daily'):
        self.pollutants = pollutants
        self.year = year
        self.state_code = state_code
        self.filter_city_list = filter_city_list
        self.lag = lag
        self.county_identifier= county_identifier
        self.plot_distribution = plot_distribution
        self.plot_distribution = "daily" if self.plot_distribution in ["daily", "monthly"] else self.plot_distribution
        self.unit_lookup = {}

    def read_pollutant(self, pollutant):
        pol_df = ReadData(pollutant, year=self.year, county_identifier=self.county_identifier,
                          observation_type=self.plot_distribution).get_pandas_obj()
        self.unit_lookup[pollutant] = pol_df['units_of_measure'].iloc[1]
        if self.state_code:
            pol_df = pol_df[pol_df['state_code'] == self.state_code]
        if self.filter_city_list:
            pol_df = pol_df[pol_df['county_code'].isin(self.filter_city_list)]
        if self.plot_distribution == 'daily':
            pol_df = pol_df.groupby(['date_local', "county", "state"]).agg({'first_max_value': 'max'}).reset_index()
            pol_df['pollutant'] = pol_df['first_max_value']
            res_df_1 = pol_df[['date_local', "county", "pollutant"]]
            res_df_1.columns = ['date', 'county', pollutant]
        elif self.plot_distribution == 'annual':
            pol_df = pol_df.groupby(['year', "county", "state"]).agg({'fourth_max_value': 'max'}).reset_index()
            pol_df['pollutant'] = pol_df['fourth_max_value']
            res_df_1 = pol_df[['year', "county", "pollutant"]]
            res_df_1.columns = ['date', 'county', pollutant]
        # if self.lag == "0-7":
        #     pol_df['pollutant'] = \
        #         pol_df.groupby(['County'])['First Max Value'].transform(lambda x: x.rolling(7).mean()).reset_index()[
        #             'First Max Value']
        return res_df_1

    def combine_pollutants(self):
        df = pd.DataFrame()
        for pollutant in self.pollutants:
            tdf = self.read_pollutant(pollutant)
            if df.empty:
                df = tdf
            else:
                df = df.merge(tdf, on=('date', 'county'), how='outer')
        return df


if __name__ == "__main__":
    """
    Earliest covid case: 2020-01-22
    AIR Pollution data till: 30-05-2020
    start_date="08-01-2019", end_date="30-05-2020"
    """
    pollutants = ["PM2", "PM10"]
    obj = CombineMultiplePollutants(pollutants,  year=2020, state_code="06", filter_city_list=["037", "111"],
                                    lag="0-14")
    print(obj.combine_pollutants())
