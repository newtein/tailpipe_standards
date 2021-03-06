from SQLAlchemyCoreClass import CoreFunctions
import math
from get_population import USPopulation


class EmissionClass:
    def __init__(self, config, county_name):
        self.config = config
        self.database = config.working_db
        self.movesouput_table = "movesoutput"
        self.core_obj = CoreFunctions(self.database, self.movesouput_table)
        obj = USPopulation()
        # self.population_lookup = obj.get(county_name)

    def calculate_emission_by_pollutant_monthly(self, start_year, end_year, pollutant_id, pollutant_name):
        query = """SELECT stateID, countyID, yearID, monthID, pollutantID, SUM(emissionQuant) as emission FROM `movesoutput` WHERE pollutantID={} and yearID BETWEEN {} and {} group by yearID, monthID, pollutantID"""
        query = query.format(pollutant_id, start_year, end_year)
        alias = ['stateID', 'countyID', 'yearID', 'monthID', 'pollutantID', 'emission']
        return list(self.core_obj.execute_query(query, alias))

    def calculate_emission_by_pollutant_yearly(self, start_year, end_year, pollutant_id, pollutant_name):
        query = """SELECT stateID, countyID, yearID, pollutantID, SUM(emissionQuant) as emission FROM `movesoutput` WHERE pollutantID={} and yearID BETWEEN {} and {} group by yearID, pollutantID"""
        query = query.format(pollutant_id, start_year, end_year)
        alias = ['stateID', 'countyID', 'yearID', 'pollutantID', 'emission']
        print(query)
        return list(self.core_obj.execute_query(query, alias))

    def get_emission(self, start_year, end_year, pollutant_id, pollutant_name):
        if self.config.plot_distribution == "monthly":
            return self.calculate_emission_by_pollutant_monthly(start_year, end_year, pollutant_id, pollutant_name)
        elif self.config.plot_distribution == "annual":
            return self.calculate_emission_by_pollutant_yearly(start_year, end_year, pollutant_id, pollutant_name)

    def test(self):
        where_payload = {
            "pollutantID": 2,
            'yearID': 2015,
            'monthID': 1,
            'dayID': 2
        }
        select_cols = ['yearID', 'monthID', 'dayID', 'emissionQuant']
        r = list(self.core_obj.select_column_where(where_payload, select_cols))
        print(r)
        print("Ceiled", sum([math.ceil(i.get('emissionQuant')) for i in r]))
        print("Floor", sum([math.floor(i.get('emissionQuant')) for i in r]))
        print("Actual", sum([i.get('emissionQuant') for i in r]))
        q = "SELECT yearID, monthID, stateID, dayID, countyID, SUM(emissionQuant) FROM `movesoutput`where pollutantID=2 and yearID=2015 and dayID=5 and monthID=1"
        alias = ['yearID', 'monthID', 'stateID', 'dayID', 'countyID', 'e']
        print(list(self.core_obj.execute_query(q, alias)))


if __name__ == "__main__":
    obj = EmissionClass('la_2015_2019')
    # print(obj.calculate_emission_by_pollutant(1))
    obj.test()
