import requests
import pandas as pd


class QueryEPAData:
    def __init__(self, key, parameter_code, state_code, start_date, end_date, county_code=None):
        """
        date format: 20200627
        """
        self.start_date = start_date
        self.end_date = end_date
        self.key = key
        self.parameter_code = parameter_code
        self.state_code = state_code
        self.county_code = county_code
        self.url = self.get_url()

    def get_url(self):
        base = "https://aqs.epa.gov/data/api"
        email = "harshitgujral12@gmail.com"
        if self.state_code and self.county_code:
            sample_url = "{}/dailyData/byCounty?email={}&key={}&param={}&bdate={}&edate={}&state={}&county={}"
            sample_url = sample_url.format(base, email, self.key, self.parameter_code, self.start_date, self.end_date,
                                           self.state_code, self.county_code)
        else:
            sample_url = "{}/dailyData/byState?email={}&key={}&param={}&bdate={}&edate={}&state={}"
            sample_url = sample_url.format(base, email, self.key, self.parameter_code, self.start_date, self.end_date,
                                           self.state_code)
        return sample_url

    def hit(self):
        r = requests.get(self.url)
        return r.json()


if __name__=="__main__":
        query_obj = QueryEPAData('ochregazelle46', '88101', '06', '20100101', '20101212', county_code='037')
        print(query_obj.hit())
