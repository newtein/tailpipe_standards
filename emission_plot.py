import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime
from copy import copy
from constants import *
import logging
import pandas as pd
import numpy as np
from geo_class import GeoClass
import seaborn as sns


class EmissionPlot:
    def __init__(self, config, df_wrapper, title=None):
        self.df_wrapper = df_wrapper
        self.config = config
        self.title = title

    def get_rows_and_cols_for_pollutants(self):
        cities = len(self.df_wrapper)
        rows, cols = cities, 1
        return rows, cols

    def make_date(self, x):
        return datetime.date(int(x['year']), int(x['month']), 1)

    def get_x_limit(self):
        xa, xb = self.config.start_year, self.config.end_year
        return datetime.date(xa, 1, 1), datetime.date(xb, 12, 31)

    def get_y_limit(self):
        ya, yb = 99, -99
        for pol in self.df_wrapper:
            t = copy(self.df_wrapper.get(pol)[self.config.pollutant_list])
            t = (t - t.mean()) / t.std()
            ya = min(ya, t.values.min())
            yb = max(yb, t.values.max())
        return ya, yb

    def get_cmap_index_pollutant(self):
        cmap = plt.get_cmap("hsv")
        n = len(self.config.pollutant_list)
        cmaps = [cmap(i) for i in self.split_into_parts(0.95, n)]
        return cmaps

    def split_into_parts(self, number, n_parts):
        return np.linspace(0, number, n_parts + 1)[1:]

    def get_image_title(self, state_id, county_id):
        geo_obj = GeoClass()
        return "{}, {}".format(geo_obj.get_county_name(county_id), geo_obj.get_state_name(state_id))

    def get_annot(self, int):
        return "{})".format(chr(97+int))

    def plot_pollutants(self):
        sns.set_style("white")
        df_wrapper = copy(self.df_wrapper)
        rows, cols = self.get_rows_and_cols_for_pollutants()
        posCord = [(i, j) for i in range(0, rows) for j in range(0, cols)]
        plt.close()
        plt.figure(figsize=(9, 8), dpi=600)
        gs = gridspec.GridSpec(rows, cols)
        xa, xb = self.get_x_limit()
        ya, yb = self.get_y_limit()
        cmaps = self.get_cmap_index_pollutant()
        for index, county in enumerate(df_wrapper):
            county_df = df_wrapper.get(county)
            county_df['date'] = county_df.apply(self.make_date, axis = 1)
            ax = plt.subplot(gs[posCord[index][0],posCord[index][1]])
            ax.text(-0.065, 0.98, self.get_annot(index), transform=ax.transAxes, size=15, color='green')
            x = county_df['date'].tolist()
            for pol_idx, pol in enumerate(self.config.pollutant_list):
                y_num = county_df[pol] - county_df[pol].mean()
                y_denum = county_df[pol].std()
                y = y_num/y_denum
                plt.plot(x, y, label=pol, color=cmaps[pol_idx], linewidth=0.8, linestyle='--')
                plt.scatter(x, y, s=5, color=cmaps[pol_idx])
            if index == 0:
                plt.legend(loc='upper right')
            plt.xlim(xa, xb)
            plt.ylim(ya-0.5, yb+0.5)
            plt.ylabel('Normalized emissions')
            # print(county, index, self.config.county, df_wrapper.keys())
            plt.title(self.config.county[index], fontsize=18)
        plt.tight_layout()
        plt.savefig(OUTPUT_FIG_DIR+"/"+self.config.get_imagename(), bbox_inches='tight')
        logging.info("Figure is saved.")

