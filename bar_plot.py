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


class BarPlot(PlotUtility):
    def __init__(self, config, df_wrapper, title=None):
        super().__init__()
        self.df_wrapper = df_wrapper
        self.config = config
        self.title = "{} ({}-{})".format(title, config.start_year, config.end_year)

    def get_rows_and_cols_for_counties(self):
        pollutants = len(self.df_wrapper)
        cols = 0
        rows = pollutants
        return rows, cols

    def plot_counties(self):
        sns.set_style("white")
        # sns.set(font_scale=1.2)
        df_wrapper = copy(self.df_wrapper)
        # rows, cols = self.get_rows_and_cols_for_counties()
        # posCord = [(i, j) for i in range(0, rows) for j in range(0, cols)]
        plt.close()
        n_height = len(self.df_wrapper)
        plt.figure(figsize=(self.width, self.height), dpi=600)
        # gs = gridspec.GridSpec(rows, cols)
        df_wrapper['County'] = df_wrapper['county']
        sns.barplot(data=df_wrapper, x="pollutant", y="efficacy", hue="County")
        plt.ylim(0, 100)

        # ax = plt.subplot(gs[posCord[index][0], posCord[index][1]])
        # ax.text(-0.065, 0.98, self.get_annot(index), transform=ax.transAxes, size=15, color='green')
        # x = county_df['pollutant'].tolist()
        # county = self.config.county[index]
        # plt.title(self.get_image_title(county), fontsize=18)
        # plt.yticks(range(len(corr.columns)), corr.columns)

        # plt.tight_layout()
        # if self.title:
        #     plt.suptitle(self.title, fontsize=16)
        #     plt.subplots_adjust(top=1.0)
        figname = self.title.replace(" ", "_") + "_bar.png"
        print(figname)
        # plt.savefig(OUTPUT_FIG_DIR + "/county_wise_" + self.config.get_imagename(), bbox_inches='tight')
        path = "{}/{}".format(OUTPUT_FIG_DIR, self.config.unique_name)
        plt.savefig(path + "/" + figname, bbox_inches='tight')
        logging.info("Figure is saved.")