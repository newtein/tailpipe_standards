from copy import copy, deepcopy
from ts_similarity_metrics import TSSimilarityMetrics
import numpy as np


class Efficacy:
    def __init__(self, config, ambient_df, onroad_df):
        self.config = config
        self.ambient_df = ambient_df
        self.onroad_df = onroad_df

    def filter_year_and_pol(self, _df, syear, eyear, pollutant):
        df = deepcopy(_df)
        f1 = (df['year'] >= syear)
        f2 = (df['year'] <= eyear)
        if self.config.plot_distribution == 'monthly':
            df = df[f1 & f2]
            df = df.sort_values(by='month')
        elif self.config.plot_distribution == 'annual':
            df = df[f1 & f2]
            df = df.sort_values(by='year')
        return df

    @staticmethod
    def scale_down_corr(corr):
        b, a = 1, 0
        max_x, min_x = 1, -1
        num = (b - a) * (corr - min_x)
        denum = max_x - min_x
        return (num/denum) + a

    def get_efficacy(self, syear, eyear, pollutant):
        ambient_df_yr = self.filter_year_and_pol(self.ambient_df, syear, eyear, pollutant)
        onroad_df_yr = self.filter_year_and_pol(self.onroad_df, syear, eyear, pollutant)
        if self.config.plot_distribution == 'annual':
            df = ambient_df_yr.merge(onroad_df_yr, on='year', how='inner')
        elif self.config.plot_distribution == 'monthly':
            df = ambient_df_yr.merge(onroad_df_yr, on=('year', 'month'), how='inner')
        contribution, efficacy = np.nan, np.nan
        if not df.empty:
            x, y = df[pollutant+"_x"].tolist(), df[pollutant+"_y"].tolist()
            similarity_obj = TSSimilarityMetrics(x, y)
            corr = similarity_obj.correlation()
            contribution = self.scale_down_corr(corr)
            efficacy = (1 - contribution)*100
        yrs = df['year'].tolist()
        report = {
            "start_year": min(yrs),
            "end_year": max(yrs),
            "pollutant": pollutant,
            "contribution": contribution,
            "efficacy": efficacy
        }
        return report

