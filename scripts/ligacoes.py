import warnings
import pandas as pd
import streamlit as st

from unidecode import unidecode
from datetime import datetime
from numpy import nan

from utils.sgdb import sgdb
from utils.settings import settings
from utils.sharepoint import Monitoramento as SharePoint

warnings.simplefilter('ignore')

class Ligacoes:
    def __init__(self) -> None:
        self.__table  : str = 'tb_ligacoes_externas'
        self.__schema : str = 'valsa'

    def __get_df(self) -> pd.DataFrame:
        site_name='monitoramento'

        mes_dict = {
            'JAN': '01', 'FEV': '02', 'MAR': '03',
            'ABR': '04', 'MAI': '05', 'JUN': '06',
            'JUL': '07', 'AGO': '08', 'SET': '09',
            'OUT': '10', 'NOV': '11', 'DEZ': '12' 
        }

        folder_name_2023 = "RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS - 2023"
        folder_name_rj_2024 = "RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - RJ"
        folder_name_mg_2024 = "RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - MG"

        file_name_2023 = "LIGAÇOES EXTERNAS 2023.xlsx"
        file_name_2024 = "LIGAÇOES EXTERNAS 2024.xlsx"

        sheet_names_2023 = ('JAN - 2023', 'FEV - 2023', 'MARÇO - 2023', 'ABRIL - 2023', 'MAIO - 2023', 'JUNHO - 2023',
                            'JULHO - 2023', 'AGOSTO - 2023', 'SETEMBRO - 2023', 'OUTUBRO - 2023', 'NOVEMBRO - 2023', 
                            'DEZEMBRO - 2023')
        
        sheet_names_2024 = ('JAN - 2024', 'FEV - 2024', 'MARÇO - 2024', 'ABRIL - 2024', 'MAIO - 2024', 'JUNHO - 2024',
                            'JULHO - 2024', 'AGOSTO - 2024', 'SETEMBRO - 2024', 'OUTUBRO - 2024', 'NOVEMBRO - 2024', 
                            'DEZEMBRO - 2024')
        
        df = pd.DataFrame()

        for sheet_name in sheet_names_2023:
            temp = SharePoint().ligacoes(file_name_2023, folder_name_2023, site_name, sheet_name=sheet_name, skiprows=1)
            mes = mes_dict.get(sheet_name.split(' ')[0][:3])
            temp['safra'] = f'2023-{mes}-01'
            temp['uf'] = 'RJ'

            df = pd.concat([df, temp])

        for sheet_name in sheet_names_2024:
            temp = SharePoint().ligacoes(file_name_2024, folder_name_rj_2024, site_name, sheet_name=sheet_name, skiprows=1)
            mes = mes_dict.get(sheet_name.split(' ')[0][:3])
            temp['safra'] = f'2024-{mes}-01'
            temp['uf'] = 'RJ'

            df = pd.concat([df, temp])

            temp = SharePoint().ligacoes(file_name_2024, folder_name_mg_2024, site_name, sheet_name=sheet_name, skiprows=1)
            mes = mes_dict.get(sheet_name.split(' ')[0][:3])
            temp['safra'] = f'2024-{mes}-01'
            temp['uf'] = 'MG'

            df = pd.concat([df, temp])

        return df

    def __datas(self, data: str) -> datetime:
        try:
            if '-' in data:
                return datetime.strptime(data.split(' ')[0], r'%Y-%m-%d')
            elif '/' in data:
                return datetime.strptime(data, r'%d/%m/%Y')
            else:
                return nan
        except:
            return nan

    def run(self) -> dict:
        with st.container():
            st.html('<h1>VALSA SAÚDE</h1>')
            st.html('<h1>LIGAÇÕES</h1>')
            with st.status('Carregando tabelas...'):
                df = self.__get_df()

            with st.status('Realizando processamento dos dados...'):
                # Columns rename
                df.columns = [unidecode(column).lower().replace(' ', '_') for column in df.columns]
                
                # Trata nome
                df['nome_do_beneficiario'] = df['nome_do_beneficiario'].fillna(df['data.1']).apply(lambda x: unidecode(str(x).upper().strip()))
                temp = df['nome_do_beneficiario'].apply(lambda x: x[0], axis=1)
                df = df.drop(columns=['nome_do_beneficiario', 'data.1'])
                df['nome_do_beneficiario'] = temp

                # Trata data
                df['data'] = df['data'].astype(str).str.split(' ').str[0].apply(self.__datas)

                # Trata plantão
                df['plantao'] = df['plantao'].fillna('nao informado').apply(lambda x: unidecode(x.upper().strip()))

            with st.status('Salvando...'):
                postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)
            if isinstance(postgre_res, int):
                st.success('Salvo com sucesso!')
            else:
                st.error(f'Erro: {postgre_res}')
