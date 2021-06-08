import requests
import pandas as pd
from constants import *


class USCensusAPI:
    def __init__(self, key):
        self.key = key
        self.url = "https://api.census.gov/data/2019/pep/population?get=COUNTY,DATE_CODE,DATE_DESC,DENSITY,POP,NAME,STATE&for=county:*&key={}"
        self.url = self.url.format(self.key)

    def get(self):
        r = requests.get(self.url)
        return r.json()

    @staticmethod
    def extract_year(x):
        return x.split()[0].split('/')[2]

    @staticmethod
    def get_state(x):
        return x.split(',')[1].strip()

    @staticmethod
    def get_county(x):
        return x.split(',')[0].strip()

    def write(self):
        data = self.get()
        headers = data[0]
        values = data[1:]
        df = pd.DataFrame(columns=headers, data=values)
        df['year'] = df['DATE_DESC'].apply(self.extract_year)
        df['state_name'] = df['NAME'].apply(self.get_state)
        df['county_name'] = df['NAME'].apply(self.get_county)
        df.to_csv(US_CENSUS_DIR+"/2010_2019_population.csv", index=False)
        return {"File written successfully."}


if __name__ == "__main__":
    with open("us_census/key.txt") as f:
        key = f.read()
    obj = USCensusAPI(key)
    print(obj.write())