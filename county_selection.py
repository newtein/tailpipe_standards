import pandas as pd
from get_population import USPopulation
from constants import *

df = pd.read_csv("states_and_counties.csv")
pop_df = pd.read_csv(CENSUS_DATA_PATH)
df['State Name'] = df['State Name'].apply(lambda x: x.lower())
pop_df['state_name'] = pop_df['state_name'].apply(lambda x: x.lower())
pop_df = pop_df[pop_df['year'] == 2019]

print(df.columns)
print(pop_df.columns)

pop_obj = USPopulation()


def if_carb(x):
    if int(x) in CARB:
        return 1
    return 0

def top_5(df):
    df = df.sort_values(by="DENSITY", ascending=False)
    df = df.drop_duplicates('county_name', keep='first')
    return df.head(20)

epa_regions = df['EPA Region'].unique().tolist()
for region in epa_regions:
    region_df = df[df['EPA Region'] == region]
    states = region_df['State Name'].unique()
    pop_df_region = pop_df[pop_df['state_name'].isin(states)]
    # print(region)
    # print(pop_df_region['state_name'].unique())
    # print(states)
    pop_df_region = pop_df_region.merge(df[['State Name', 'State Code']], left_on='state_name',
                                        right_on='State Name', how='left')
    pop_df_region['CARB'] = pop_df_region['State Code'].apply(if_carb)
    pop_df_region['surface_area'] = pop_df_region['POP']/pop_df_region['DENSITY']
    pop_df_region_carb = pop_df_region[pop_df_region['CARB'] == 1]
    pop_df_region_epa = pop_df_region[pop_df_region['CARB'] == 0]
    pop_df_region_carb = top_5(pop_df_region_carb)
    pop_df_region_epa = top_5(pop_df_region_epa)
    if not pop_df_region_epa.empty and not pop_df_region_carb.empty:
        pop_df_region_epa.to_csv(US_CENSUS_DIR+"/epa_{}.csv".format(region))
        pop_df_region_carb.to_csv(US_CENSUS_DIR+"/carb_{}.csv".format(region))


