import io
import pandas as pd
from office365.sharepoint.files.file import File
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

from utils.settings import settings

class Monitoramento:
    def _auth(self):
        url = f'{settings.SHAREPOINT_URL}/monitoramento'
        user = settings.SHAREPOINT_EMAIL
        pwd = settings.SHAREPOINT_PWD
        conn = ClientContext(url).with_credentials(UserCredential(user, pwd))
        return conn

    def get_file(self, file_name, folder_name, site_name, sheet_name=None, skiprows=0) -> pd.DataFrame:
        conn = self._auth()
        file_url = f'/sites/{site_name}/Shared Documents/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        # Convert binary content to Pandas DataFrame
        df = pd.read_excel(io.BytesIO(file.content), sheet_name=sheet_name, 
                           skiprows=skiprows, engine='openpyxl')
        
        return pd.concat(df.values(), ignore_index=True)
    
    def ligacoes(self, file_name, folder_name, site_name, sheet_name=None, skiprows=0) -> pd.DataFrame:
        conn = self._auth()
        file_url = f'/sites/{site_name}/Shared Documents/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        # Convert binary content to Pandas DataFrame
        df = pd.read_excel(io.BytesIO(file.content), sheet_name=sheet_name, 
                           skiprows=skiprows, engine='openpyxl')
        
        return df
    

class Analytics:
    def _auth(self):
        conn = ClientContext(f'{settings.SHAREPOINT_URL}/Analytics').with_credentials(
            UserCredential(settings.SHAREPOINT_EMAIL, settings.SHAREPOINT_PWD)
        )
        return conn

    def get_file(self, file_name, folder_name, site_name, type_read='concat', sheet_name=None) -> pd.DataFrame:
        conn = self._auth()
        file_url = f'/sites/{site_name}/Documentos Compartilhados/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        # Convert binary content to Pandas DataFrame
        df = pd.read_excel(io.BytesIO(file.content), sheet_name=sheet_name, engine='openpyxl')
        if type_read == 'concat':
            return pd.concat(df.values(), ignore_index=True)
        else:
            return df
    
    def linha_cuidados(self, file_name, folder_name, site_name, sheet_name=None) -> pd.DataFrame:
        conn = self._auth()
        file_url = f'/sites/{site_name}/Documentos Compartilhados/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        # Convert binary content to Pandas DataFrame
        df = pd.read_excel(io.BytesIO(file.content), sheet_name=sheet_name, engine='openpyxl')
        return df
