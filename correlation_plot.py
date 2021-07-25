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


class CorrelationPlot(PlotUtility):
    def __init__(self, config, df_wrapper, title=None):
        super().__init__()
        self.df_wrapper = df_wrapper
        self.config = config
        self.title = "{} ({}-{})".format(title, config.start_year, config.end_year)

    def get_rows_and_cols_for_counties(self):
        pollutants = len(self.config.pollutant_list)
        cols = 2
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

    def get_image_title(self, county_name):
        # geo_obj = GeoClass()
        # county_name = geo_obj.get_county_name(county_id)
        # state_name = geo_obj.get_state_name(state_id)
        standard_name = self.config.get_standards(county_name)
        return "{}: {}".format(standard_name, county_name.replace("County", "").strip())

    def plot_counties(self):
        sns.set_style("white")
        # sns.set(font_scale=1.2)
        df_wrapper = copy(self.df_wrapper)
        rows, cols = self.get_rows_and_cols_for_counties()
        posCord = [(i, j) for i in range(0, rows) for j in range(0, cols)]
        plt.close()
        n_height = math.ceil(len(self.config.county)/2)
        plt.figure(figsize=(self.width*1.3, self.get_corr_height(n_height)*2), dpi=600)
        gs = gridspec.GridSpec(rows, cols)
        cmap = plt.get_cmap("GnBu")
        for index, county in enumerate(df_wrapper):
            county_df = df_wrapper.get(county)
            county_df['date'] = county_df.apply(self.make_date, axis=1)
            ax = plt.subplot(gs[posCord[index][0], posCord[index][1]])
            ax.text(-0.065, 0.98, self.get_annot(index), transform=ax.transAxes, size=15, color='green')
            x = county_df['date'].tolist()
            corr = county_df[self.config.pollutant_list].corr()
            corr.columns = [i.replace(" ","\n") for i in corr.columns]
            mask = np.triu(np.ones_like(corr, dtype=np.bool))
            properties = {
                "vmin": -1,
                "vmax": 1,
                "annot": True,
                "square": True,
                "cmap": cmap,
                "cbar_kws" : {"shrink": 0.2},
                "mask": mask
                #"annot_kws": {"size": 12}
            }
            if index % 2 == 0:
                # properties.update({"cbar": False})
                sns.heatmap(corr, **properties)
                plt.ylabel('{} emissions'.format(self.config.plot_distribution.capitalize()))
            else:
                sns.heatmap(corr, **properties)
            county = self.config.county[index]
            plt.title(self.get_image_title(county), fontsize=18)
            #plt.yticks(range(len(corr.columns)), corr.columns)
        plt.tight_layout()
        if self.title:
            plt.suptitle(self.title, fontsize=16)
            plt.subplots_adjust(top=1.2)
        figname = self.title.replace(" ", "_")+"_corr.png"
        print(figname)
        # plt.savefig(OUTPUT_FIG_DIR + "/county_wise_" + self.config.get_imagename(), bbox_inches='tight')
        path = "{}/{}".format(OUTPUT_FIG_DIR, self.config.unique_name)
        plt.savefig(path + "/" + figname, bbox_inches='tight')
        logging.info("Figure is saved.")