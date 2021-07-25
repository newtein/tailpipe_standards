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
import math
from get_cmap import GetCmap
from scipy import stats
from plot_utility import PlotUtility


class CountyPlot(PlotUtility):
    def __init__(self, config, df_wrapper, title=None, pollutant_units=None):
        print(config.fac, "?????????????????????")
        super().__init__(fac=config.fac)
        self.df_wrapper = df_wrapper
        self.config = config
        self.title = "{} ({}-{})".format(title, config.start_year, config.end_year)
        self.pollutant_units = pollutant_units

    def get_rows_and_cols_for_counties(self):
        pollutants = len(self.config.pollutant_list)
        cols = 3
        rows = math.ceil(pollutants/cols)
        return rows, cols

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

    def split_into_parts(self, number, n_parts):
        return np.linspace(0, number, n_parts + 1)[1:]

    def get_image_title(self, county_name):
        # geo_obj = GeoClass()
        # county_name = geo_obj.get_county_name(county_id)
        # state_name = geo_obj.get_state_name(state_id)
        standard_name = self.config.get_standards(county_name)
        return "{}: {}".format(standard_name, county_name.replace("County", "").strip())

    def get_annot(self, int):
        return "{})".format(chr(97 + int))

    def normalize(self, df, col):
        return (df[col] - df[col].mean()) / df[col].std()

    def regression_line(self, x, y):
        x_vals = np.array(list(range(1, len(x)+1)))
        res = stats.linregress(x_vals, y)
        y_vals = res.intercept + res.slope * x_vals
        return x, y_vals

    def plot_counties(self):
        sns.set_style("white")
        df_wrapper = copy(self.df_wrapper)
        rows, cols = self.get_rows_and_cols_for_counties()
        posCord = [(i, j) for i in range(0, rows) for j in range(0, cols)]
        plt.close()
        n_height = math.ceil(len(self.config.pollutant_list)/3)
        plt.figure(figsize=(self.width*1.7, self.get_height(n_height)), dpi=600)
        gs = gridspec.GridSpec(rows, cols)
        cmap_obj = GetCmap(self.config)

        for index, pollutant in enumerate(self.config.pollutant_list):
            ax = plt.subplot(gs[posCord[index][0], posCord[index][1]])
            ax.text(-0.07, 1.03, self.get_annot(index), transform=ax.transAxes, size=self.annot_size, color='black')
            for db_idx, db in enumerate(df_wrapper):
                pollutant_df = df_wrapper.get(db)
                pollutant_df['date'] = pollutant_df.apply(self.make_date, axis=1)
                x = pollutant_df['date'].tolist()
                # y = self.normalize(pollutant_df, pollutant)
                y = pollutant_df[pollutant].tolist()
                county_name = self.config.county[db_idx]
                cmap = cmap_obj.get_county_cmap(county_name)
                plt.plot(x, y, color=cmap, linewidth=self.linewidth, linestyle='--')
                plt.scatter(x, y, s=self.s, color=cmap)
                plt.plot([], [], marker="o", ms=self.ms, ls="", color=cmap, label=self.get_image_title(county_name))
                reg_x, reg_y = self.regression_line(x, y)
                plt.plot(reg_x, reg_y, color=cmap, linewidth=self.reg_line, linestyle="dotted")
                xtic = list(map(lambda x:x.year, x))
                plt.xticks(fontsize=self.xticks, rotation=20)
                plt.yticks(fontsize=self.xticks)
            if index == self.config.legend_pos:
                plt.legend(loc=self.config.legend_loc, frameon=False, prop={'size': self.legend})
            flag = 0
            if self.pollutant_units:
                flag = 1
            ylabel, plot_distribution = "{} emissions ({})", self.config.plot_distribution.capitalize()
            ylabel = ylabel.format(plot_distribution, "grams") if flag != 1 else ylabel.format(plot_distribution, self.pollutant_units[pollutant])
            plt.ylabel(ylabel, fontsize=self.xticks)
            plt.title(pollutant, fontsize=18)
        plt.tight_layout()
        if self.title:
            plt.suptitle(self.title, fontsize=22, y=1.05)
            # plt.subplots_adjust(top=0.85)
        figname = self.title.replace(" ", "_")+"_pol.png"
        path = "{}/{}".format(OUTPUT_FIG_DIR, self.config.unique_name)
        plt.savefig(path + "/" + figname, bbox_inches='tight')
        logging.info("Figure is saved.")