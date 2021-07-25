import matplotlib.pyplot as plt
import numpy as np


class GetCmap:
    def __init__(self, config):
        self.config = config

    def split_cmap(self, cmap, n):
        return [cmap(i) for i in self.split_into_parts(0.95, n)]

    def split_into_parts(self, number, n_parts):
        return np.linspace(0, number, n_parts + 1)[1:]

    def get_county_cmap(self, county_name):
        carb_cmap = plt.get_cmap("Greens")
        epa_cmap = plt.get_cmap("Reds")
        n = len(self.config.county)
        carb_cmaps = self.split_cmap(carb_cmap, n)
        epa_cmaps = self.split_cmap(epa_cmap, n)
        if county_name in self.config.epa_county:
            index = self.config.epa_county.index(county_name)
            return epa_cmaps[index]
        elif county_name in self.config.carb_county:
            index = self.config.carb_county.index(county_name)
            return carb_cmaps[index]
