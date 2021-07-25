import datetime


class PlotUtility:
    def __init__(self, fac=1):
        self.linewidth = 1.6*fac
        self.s = 6.9*fac
        self.ms = 11.5*fac
        self.legend = 13.8*fac
        self.reg_line = 1.38*fac
        self.xticks = 12.65*fac
        self.width = 10
        self.height = 4
        self.corr_height = 16
        self.annot_size = 15*fac

    def make_date(self, x):
        if 'month' in x:
            return datetime.date(int(x['year']), int(x['month']), 1)
        else:
            return datetime.date(int(x['year']), 1, 1)

    def get_height(self, n):
        return self.height*n

    def get_corr_height(self, n):
        return self.corr_height * n
