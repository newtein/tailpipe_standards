from SQLAlchemyCoreClass import CoreFunctions


class GeoClass:
    def __init__(self):
        db = 'movesdb20210209'
        self.county_tableobj = CoreFunctions(db, 'county')
        self.state_tableobj = CoreFunctions(db, 'state')

    def get_county_name(self, county_id):
        where_payload = {
            "countyID": county_id
        }
        select_cols = ['countyName']
        rs = next(self.county_tableobj.select_column_where(where_payload, select_cols))
        return rs.get(select_cols[0]).replace("County", "").strip()

    def get_state_name(self, state_id):
        where_payload = {
            "stateID": state_id
        }
        select_cols = ['stateName']
        rs = next(self.state_tableobj.select_column_where(where_payload, select_cols))
        return rs.get(select_cols[0])