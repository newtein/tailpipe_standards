from SQLAlchemyCoreClass import CoreFunctions


class Pollutant:
    def __init__(self):
        self.pollutant_tablename = "pollutant"
        self.pollutant_table_obj = CoreFunctions('movesdb20210209', 'pollutant')


    def sanitize(self, pollutant_list):
        pollutants = {i.get("shortName") for i in self.pollutant_table_obj.select_column(["shortName"])}
        error = 0
        for input_pollutant in pollutant_list:
            if input_pollutant not in pollutants:
                error = 1
                break
        msg = "Input pollutants matched." if error == 0 else "Pollutant {} does not match.".format(input_pollutant)
        return {'error': error, "msg": msg}

    def get_id_from_shortname(self, shortname):
        where_payload = {
            "shortName": shortname,
        }
        select_column = ['pollutantID']
        result = next(self.pollutant_table_obj.select_column_where(where_payload, select_column))
        return result.get(select_column[0])

