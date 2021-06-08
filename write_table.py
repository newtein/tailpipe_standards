import csv
import os
import datetime


class WriteTable:
    def __init__(self, config_filename):
        self.config_filename = config_filename
        filename = "{}/{}"
        pass

    def get_write_filename(self):
        fname, ext = os.path.splitext(self.config_filename)
        return "fname_emission"