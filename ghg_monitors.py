from query_data import QueryEPAData
import pandas as pd

if __name__ == "__main__":

    df = pd.read_csv("states_and_counties.csv", dtype=str)
    state_codes = df['State Code'].unique().tolist()

    for code in state_codes:
        query_obj = QueryEPAData('ochregazelle46', '42102', code, '20190101', '20191212', plot_distribution='annual')
        rs = query_obj.hit()
        data = rs.get('Data')
        if data:
            print(code, "successful")



