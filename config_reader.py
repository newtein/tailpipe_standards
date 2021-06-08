

class ConfigReader:
    def __init__(self, filename):
        self.input_config = eval(open(filename, "r").read())
        self.start_year, self.end_year = self.input_config.get("start_year"), self.input_config.get("end_year")
        self.pollutant_list = self.input_config.get("pollutant")
        self.db = self.input_config.get("database")
        self.county = self.input_config.get("county")
        self.state = self.input_config.get("state")
        self.epa_county = self.input_config.get("EPA")
        self.carb_county = self.input_config.get("CARB")
        self.plot_distribution = self.input_config.get("plot_distribution")
        self.working_db = self.unwrap_dbs()[0]
        self.unique_name = self.input_config.get("unique_name")
        self.legend_loc = self.input_config.get("legend_loc")
        self.population_adjusted = self.input_config.get("population_adjusted", False)
        self.figure_title = self.input_config.get("figure_title", None)
        self.legend_pos = self.input_config.get("legend_pos", 0)

    def unwrap_dbs(self):
        db = []
        for index, i in enumerate(self.db):
            if type(i) == list:
                for j in i:
                    db.append((index, j))
            else:
                db.append((index, i))
        return db

    def get_column_names(self):
        if self.plot_distribution == 'monthly':
            columns = ['year', 'month']
        elif self.plot_distribution == 'yearly':
            columns = ['year']
        columns = columns + self.pollutant_list
        return columns

    def name_list(self):
        if self.unique_name:
            return [self.unique_name]
        return [self.start_year, self.end_year]+self.get_column_names()

    def get_filename(self, c=''):
        list_values = [c] + self.name_list() + [".csv"]
        return "_".join(map(str, list_values))

    def get_imagename(self):
        list_values = self.name_list() + [".png"]
        return "_".join(map(str, list_values))

    def get_start_end_years(self, db):
        years_info = self.input_config.get(db, None)
        if years_info:
            return years_info.get("start_year"), years_info.get("end_year")
        return self.start_year, self.end_year

    def get_standards(self, county_name):
        if county_name in self.epa_county:
            return "EPA"
        elif county_name in self.carb_county:
            return "CARB"
