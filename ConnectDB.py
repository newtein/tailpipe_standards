from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker



class ConnectDB:

    def __init__(self, database):
        self._dbconfig = {
        "username": "root",
        "pwd": "",
        "host": "localhost",
        "dbname": database
        }
        con_string = "mysql+pymysql://{0}:{1}@{2}/{3}".format(self._dbconfig['username'], self._dbconfig['pwd'],
                                                                    self._dbconfig['host'], self._dbconfig['dbname'])
        self._dbengine = create_engine(con_string, echo=False)
        # self._dbengine = create_engine(con_string, echo=True)
        self._metadata = {}

    def get_dbengine(self):
        return self._dbengine

    def get_session(self):
        Session = sessionmaker(bind=self._dbengine)
        dbsession = scoped_session(Session)
        return dbsession

    def get_metadata(self):
        meta = MetaData()
        # meta.reflect(bind=self._dbengine)
        return meta



if __name__ == "__main__":
    obj = ConnectDB()
    print(obj.get_dbengine())