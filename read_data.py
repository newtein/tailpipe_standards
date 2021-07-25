import pandas as pd
from copy import copy, deepcopy
from constants import *


class ReadData:
    def __init__(self, pollutant, year='2020', observation_type="daily", filename=None, county_level=False,
                 county_identifier=None):
        """
        PM10 Ozone NO2 SO2 CO
        parameters = ["81102", "44201", "42602", "42401", "42101"]
        """
        self.year = year
        self.pollutant = pollutant
        self.observation_type = observation_type
        self.filename = filename
        self.county_level = county_level
        self.county_identifier = county_identifier
        self.pollutant_map = {
            "CO": "42101",
            "S02": "42401",
            "NO2": "42602",
            "O3": "44201",
            "PM10": "81102",
            "PM2": "88101",
            "WIND": "61103",
            "TEMP": "68105",
            "RH": "62201",
            "Pressue": "68108"
        }
        # {'Aqi': 'first','Method Code': 'first',  'First Max Hour': 'first',}
        self.agg_prototype = {
                             'Arithmetic Mean': 'first',
                             'Cbsa': 'first',
                             'Cbsa Code': 'first',
                             'City': 'first',
                             'County': 'first',
                             'County Code': 'first',
                             'Date Of Last Change': 'first',
                             'Datum': 'first',
                             'Event Type': 'first',

                             'First Max Value': 'first',
                             'Latitude': 'first',
                             'Local Site Name': 'first',
                             'Longitude': 'first',
                             'Method': 'first',

                             'Observation Count': 'first',
                             'Observation Percent': 'first',
                             'Parameter': 'first',
                             'Parameter Code': 'first',
                             'Poc': 'first',
                             'Pollutant Standard': 'first',
                             'Sample Duration': 'first',
                             'Site Address': 'first',
                             'Site Number': 'first',
                             'State': 'first',
                             'State Code': 'first',
                             'Units Of Measure': 'first',
                             'Validity Indicator': 'first'}
        self.agg_prototype = {i.lower().replace(" ", "_"): j for i, j in self.agg_prototype.items()}

    def get_file_name(self):
        pollutant_code = self.pollutant_map.get(self.pollutant, self.pollutant)
        fname = "{}_{}_{}".format(self.observation_type,pollutant_code, self.year)
        if self.county_identifier:
            fname = "{}_{}".format(fname, self.county_identifier)
        return "{}/{}.csv".format(AMBIENT_AIR_DATA, fname)

    def create_id(self, x):
        if self.county_level:
            _id = "{}_{}".format(x['state_code'], x['county_code'])
            return _id
        _id = "{}_{}_{}".format(x['state_code'], x['county_code'], x['site_number'])
        return _id

    def get_pandas_obj(self):
        """
        "State Code","County Code","Site Num"
        """
        filename = self.filename if self.filename else self.get_file_name()
        str_cols = ['state_code', 'county_code', 'site_number']
        str_dict = {i: str for i in str_cols}
        df = pd.read_csv(filename, dtype=str_dict)
        df['id'] = df.apply(self.create_id, axis=1)
        sample_duration = ['24-HR BLK AVG', '24 HOUR']
        # df = df[df['Sample Duration'].isin(sample_duration)]
        if self.observation_type == 'daily':
            df['date_local'] = pd.to_datetime(df['date_local'], format='%Y-%m-%d')
            self.agg_prototype.update({'first_max_value': 'max', 'arithmetic_mean': 'max', 'aqi': 'max'})
            df = df.groupby(['id', 'date_local']).agg(self.agg_prototype).reset_index()
            df = df.sort_values(by='date_local')
        elif self.observation_type == 'annual':
            self.agg_prototype.update({'fourth_max_value': 'max', 'arithmetic_mean': 'max'})
            df = df.groupby(['id', 'year']).agg(self.agg_prototype).reset_index()
            df = df.sort_values(by='year')
        # self.agg_prototype.pop('Poc')
        # df = df[df['Sample Duration']=='24-HR BLK AVG']
        return df


if __name__ == "__main__":
    obj = ReadData('PM2', year='2020')
    print (obj.get_pandas_obj().head(2))
