# Bibliotecas
import pyodbc
import warnings
import pandas as pd

from sqlalchemy import create_engine
from utils.settings import settings

warnings.filterwarnings("ignore")

class SGDB:
    def postgre(self, df: pd.DataFrame, table: str, schema: str) -> int|str:
        payload: dict = {
            'dialect'   : 'postgresql',
            'drive'     : 'psycopg2',
            'host'      : settings.DL_HOST ,
            'user'      : settings.DL_USER ,
            'pwd'       : settings.DL_PWD,
            'database'  : settings.DL_DATABASE
        }

        try:
            con = create_engine(self.__get_url(payload))
            return df.to_sql(name=table, con=con, schema=schema, if_exists='replace', index=False)
        except Exception as e:
            return str(e)
    
    def read_lakehouse(self, query: str) -> pd.DataFrame:
        payload: dict = {
                    'dialect'   : 'postgresql',
                    'drive'     : 'psycopg2',
                    'host'      : settings.DL_HOST ,
                    'user'      : settings.DL_USER ,
                    'pwd'       : settings.DL_PWD,
                    'database'  : settings.DL_DATABASE
                }

        try:
            con = create_engine(self.__get_url(payload))
            return pd.read_sql(query, con=con)
        except Exception as e:
            return str(e)

    def mssql(self, query: str) -> pd.DataFrame:
        payload: dict = {
                'dialect'   : 'mssql',
                'drive'     : settings.MS_ODBC,
                'host'      : settings.HMAP_HOST,
                'user'      : settings.HMAP_USER,
                'pwd'       : settings.HMAP_PWD,
                'database'  : settings.HMAP_DATABASE
            }
        
        try:
            con = pyodbc.connect(self.__get_url(payload, True))
            return pd.read_sql(query, con=con)
        except Exception as e:
            return str(e)

    def mssql_pep(self, query: str) -> pd.DataFrame:
        payload: dict = {
                'dialect'   : 'mssql',
                'drive'     : settings.MS_ODBC,
                'host'      : settings.HMAP_HOST,
                'user'      : settings.HMAP_USER_PEP,
                'pwd'       : settings.HMAP_PWD_PEP,
                'database'  : settings.HMAP_DATABASE
            }

        try:
            con = pyodbc.connect(self.__get_url(payload, True))
            return pd.read_sql(query, con=con)
        except Exception as e:
            return str(e)
        
    def __get_url(self, payload: dict, fl_mssql: bool = False) -> str:
        dialect : str    = payload.get('dialect')
        drive   : str    = payload.get('drive')
        user    : str    = payload.get('user')
        pwd     : str    = payload.get('pwd')
        host    : str    = payload.get('host')
        database: str    = payload.get('database')

        if not fl_mssql:
            return f'{dialect}+{drive}://{user}:{pwd}@{host}/{database}'
        else:
            return f'Driver={drive};Server={host};PORT=1433;Encrypt=no;UID={user};PWD={pwd}'
sgdb = SGDB()
