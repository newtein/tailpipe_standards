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


class CountyBoxplot:
    def __init__(self, config, df_wrapper, title=None):
        self.df_wrapper = df_wrapper
        self.config = config
        self.title = "{} ({}-{})".format(title, config.start_year, config.end_year)

    def get_rows_and_cols_for_counties(self):
        pollutants = len(self.config.pollutant_list)
        cols = 2
        rows = math.ceil(pollutants/cols)
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

    def set_box_color(self, bp, color):
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        plt.setp(bp['medians'], color=color)

    def plot_counties(self):
        sns.set_style("white")
        df_wrapper = copy(self.df_wrapper)
        rows, cols = self.get_rows_and_cols_for_counties()
        posCord = [(i, j) for i in range(0, rows) for j in range(0, cols)]
        plt.close()
        plt.figure(figsize=(13, 5), dpi=600)
        gs = gridspec.GridSpec(rows, cols)
        xa, xb = self.get_x_limit()
        ya, yb = self.get_y_limit()
        cmap_obj = GetCmap(self.config)

        for index, pollutant in enumerate(self.config.pollutant_list):
            ax = plt.subplot(gs[posCord[index][0], posCord[index][1]])
            ax.text(-0.07, 0.98, self.get_annot(index), transform=ax.transAxes, size=15, color='black')
            for db_idx, db in enumerate(df_wrapper):
                pollutant_df = df_wrapper.get(db)
                pollutant_df['date'] = pollutant_df.apply(self.make_date, axis=1)
                x_ticks = range(self.config.start_year, self.config.end_year+1)
                x = list(range(len(x_ticks)))
                # y = pollutant_df[pollutant].tolist()
                y = pollutant_df[['year', 'month', pollutant]].groupby('year')[pollutant].apply(list).reset_index()[pollutant].tolist()
                county_name = self.config.county[db_idx]
                cmap = cmap_obj.get_county_cmap(county_name)
                num = len(self.config.pollutant_list)
                positions = np.array(x)*num - 0.6*num + 0.6*(db_idx+1)
                bplt = plt.boxplot(y, sym='', widths=0.5, positions=positions)
                self.set_box_color(bplt, cmap)
                plt.plot([], [], marker="o", ms=10, ls="", color=cmap, label=self.get_image_title(county_name))
                x_val = range(0, len(x)*num, num)
                plt.xticks([i - 0.9 for i in x_val], x_ticks)

            if index == self.config.legend_pos:
                plt.legend(loc=self.config.legend_loc, frameon=False)
            if index % 2 == 0:
                plt.ylabel('Monthly emissions')
            plt.title(pollutant, fontsize=18)
        plt.tight_layout()
        if self.title:
            plt.suptitle(self.title, fontsize=22, y=1.05)
            # plt.subplots_adjust(top=0.85)
        figname = self.title.replace(" ", "_")+"_boxplot.png"
        # plt.savefig(OUTPUT_FIG_DIR + "/county_wise_" + self.config.get_imagename(), bbox_inches='tight')
        plt.savefig(OUTPUT_FIG_DIR + "/" + figname, bbox_inches='tight')
        logging.info("Boxplot is saved.")