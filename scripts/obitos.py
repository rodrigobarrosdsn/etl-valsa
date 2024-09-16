import warnings
import pandas as pd
import streamlit as st

from unidecode import unidecode
from datetime import datetime
from numpy import nan

from utils.sharepoint import Monitoramento as SharePoint
from utils.sgdb import sgdb

warnings.simplefilter('ignore')

class Obitos:
    def __init__(self) -> None:
        self.__table  : str = 'tb_obitos'
        self.__schema : str = 'valsa'

    def __make_query(self) -> pd.DataFrame:
        site_name = 'monitoramento'
        folder_name_rj_2024 = 'RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - RJ'
        folder_name_mg_2024 = 'RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - MG'
        file_name_2024 = 'PLANILHA DE OBITO 2024.xlsx'

        mes_dict = {
            'JAN': '01', 'FEV': '02', 'MAR': '03',
            'ABR': '04', 'MAI': '05', 'JUN': '06',
            'JUL': '07', 'AGO': '08', 'SET': '09',
            'OUT': '10', 'NOV': '11', 'DEZ': '12' 
        }

        sheet_names_2024 = ('JANEIRO - 2024', 'FEVEREIRO - 2024', 'MARÇO - 2024', 'ABRIL - 2024',
                            'MAIO - 2024', 'JUNHO - 2024', 'JULHO - 2024', 'AGOSTO - 2024', 
                            'SETEMBRO - 2024', 'OUTUBRO - 2024', 'NOVEMBRO - 2024', 'DEZEMBRO - 2024')

        df = pd.DataFrame()
        for sheet_name in sheet_names_2024:
            temp = SharePoint().ligacoes(file_name_2024, folder_name_rj_2024, 
                                         site_name, sheet_name=sheet_name,
                                         skiprows=0)

            temp['safra'] = f'2024-{mes_dict.get(sheet_name.split(" ")[0][:3])}-01'
            temp['uf'] = 'RJ'
            temp.columns = [unidecode(column).lower().replace(' ', '_').strip() for column in temp.columns]
            
            df = pd.concat([df, temp])

            temp = SharePoint().ligacoes(file_name_2024, folder_name_mg_2024, 
                                         site_name, sheet_name=sheet_name,
                                         skiprows=1)

            temp['safra'] = f'2024-{mes_dict.get(sheet_name.split(" ")[0][:3])}-01'
            temp['uf'] = 'MG'
            temp.columns = [unidecode(column).lower().replace(' ', '_').strip() for column in temp.columns]
            df = pd.concat([df, temp])

        return df

    def __datas(self, data: str) -> datetime:
        try:
            if '-' in data:
                return datetime.strptime(data.split(' ')[0], r'%Y-%m-%d')
            else:
                return datetime.strptime(data, r'%d/%m/%Y')
        except:
            return nan

    def run(self, anos: int) -> dict:
        with st.container():
            st.html('<h1>ÓBITOS</h1>')
            with st.status('Carregando as tabelas...'):
                df = self.__make_query()
            
            with st.status('Realizando o processamento dos dados...'):
                # Tratamento das datas
                df['data_do_obito'] = df['data_do_obito'].astype(str).apply(self.__datas)
                df['data'] = df['data'].astype(str).apply(self.__datas)

                # Normalização dos nomes
                df['beneficiario'] = df['beneficiario'].apply(lambda x: unidecode(x.upper().strip()))

                # Exclusão de colunas
                df = df.drop(columns=['iw'])
            
            with st.status('Salvando...'):
                postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)
            if isinstance(postgre_res, int):
                st.success('Salvo com sucesso!')
            else:
                st.error(f'Erro: {postgre_res}')
