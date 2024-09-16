import re
import warnings
import streamlit as st
import pandas as pd

from unidecode import unidecode
from datetime import datetime
from numpy import nan

from utils.sgdb import sgdb
from utils.sharepoint import Monitoramento as SharePoint

warnings.simplefilter('ignore')

class Hospitalizacao:
    def __init__(self) -> None:
        self.__table  : str = 'tb_hospitalizacao'
        self.__schema : str = 'valsa'

    def __make_query(self) -> pd.DataFrame:
        site_name = 'monitoramento'
        folder_name_rj_2024 = 'RJ - Melhor Idade\PLANILHA VALSA\PLANILHAS VALSA 2024\PLANILHAS VALSA 2024 - RJ'
        folder_name_mg_2024 = 'RJ - Melhor Idade\PLANILHA VALSA\PLANILHAS VALSA 2024\PLANILHAS VALSA 2024 - MG'
        file_name_rj_2024 = 'HOSPITALIZADOS.xlsx'
        file_name_mg_2024 = 'CONTROLE DE HOSPITALIZAÇÃO 2024.xlsx'

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
            temp = SharePoint().ligacoes(file_name_rj_2024, folder_name_rj_2024, 
                                         site_name, sheet_name=sheet_name,
                                         skiprows=2)
            
            temp['mes_safra'] = mes_dict.get(sheet_name.split(" ")[0][:3])
            temp['ano_safra'] = 2024
            temp['uf'] = 'RJ'
            temp.columns = [unidecode(column).lower().replace(' ', '_').strip() for column in temp.columns]
            temp.rename(columns={'classificacao': 'classificacao_de_risco'}, inplace=True)
            df = pd.concat([df, temp])

            temp = SharePoint().ligacoes(file_name_mg_2024, folder_name_mg_2024, 
                                         site_name, sheet_name=sheet_name,
                                         skiprows=1)

            temp['mes_safra'] = mes_dict.get(sheet_name.split(" ")[0][:3])
            temp['ano_safra'] = 2024
            temp['uf'] = 'MG'
            temp.columns = [unidecode(column).lower().replace(' ', '_').strip() for column in temp.columns]
            temp.rename(columns={'data_internacao': 'data_da_internacao'}, inplace=True)
            df = pd.concat([df, temp])

        return df

    def __datas(self, data: str) -> datetime:
        data = data.strip()
        try:
            if '-' in data:
                return datetime.strptime(data.split(' ')[0], r'%Y-%m-%d')
            elif '/' in data:
                return datetime.strptime(data, r'%d/%m/%Y')
            else:
                return nan
        except:
            return nan

    def __alta(self, df: pd.DataFrame) -> datetime:
        res = ''
        padrao_data = r'\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{1,2}-\d{1,2}'
        alta = str(df['data_alta'])
        obs = df['observacao']
    
        if len(alta) > 3:
            res = alta
        else:
            for chave in ('ALTA', 'OBITO'):
                if chave in str(obs):
                    res = ''.join(obs.split(chave)[1:])
                else:
                    pass
        data = ''.join(re.findall(padrao_data, str(res)))
        return self.__datas(data)
    
    def __get_hospitalizacoes(self, matricula: str, df: pd.DataFrame) -> pd.DataFrame:
        res = pd.DataFrame()
        temp = df.query(f'matricula == "{matricula}"')
        datas = temp.data_da_internacao.unique()
        for data in datas:
            selecao = temp.query(f'data_da_internacao == "{data}"')
            selecao = selecao.query('ano_safra == ano_safra.max()')
            selecao = selecao.query('mes_safra == mes_safra.max()')
            res = pd.concat([res, selecao])
        return res

    def __tempo_internacao(self, df: pd.DataFrame) -> int:
        internacao = df['data_da_internacao']
        alta = df['data_alta']
        dias_internado = df['tempo_de_internacao']
    
        if isinstance(dias_internado, int):
            return dias_internado
        elif isinstance(dias_internado, float):
            try:
                return abs(int(round((alta - internacao).days, 0)))
            except:
                return -1
        elif isinstance(dias_internado, str):
            return -2
        else:
            return -3

    def __classificacao(self, x: str) -> str:
        x = unidecode(str(x)).upper().strip()
        if 'BUST' in x:
            return 'ROBUSTO'
        elif 'PARCI' in x or 'SEVER' in x:
            return 'PARCIAL'
        elif 'FRA' in x:
            return 'FRAGIL'
        else:
            return nan
            
    def __hospital(self, x: str) -> str:
        x = unidecode(x.upper().strip())
        if (x == 'CASA' or 'RESIDENCIA' in x) or ('DENCIA' in x):
            return 'RESIDENCIA'
        else:
            return x

    def __eletivo(self, tipo: str) -> str:
        tipo = unidecode(tipo).upper().strip()
        if 'EMERG' in tipo:
            return 'EMERGENCIA'
        elif 'ELE' in tipo:
            return 'ELETIVO'
        else:
            return tipo
            
    def run(self, anos: tuple) -> dict:
        with st.container():
            st.html('<h1>HOSPITALIZAÇÃO</h1>')
            with st.status('Carregando tabelas...'):
                # Leitura das tabelas
                df = self.__make_query()

            with st.status('Realizando processamento dos dados...'):
                # Remoção de beneficiários sem nome
                df = df.query('beneficiario.notna()')

                # Renome
                df = df.rename(columns={'aph?': 'aph', 'eletivo?': 'eletivo'})

                # Normalização de strings
                df['beneficiario'] = df['beneficiario'].apply(lambda x: unidecode(x.upper().strip()))
            
                # Tratamento de datas
                df['data_da_internacao'] = df['data_da_internacao'].astype(str)
                df['data_da_internacao'] = df['data_da_internacao'].fillna(df['data_internacao'].astype(str)).astype(str).str.strip().apply(self.__datas)

                # Tratamento de matricula
                df['matricula'] = df['matricula'].astype(str)

                # Remoção de variáveis desnecessárias
                colunas = ['unnamed:_11', 'data_internacao']
                df.drop(columns=colunas, inplace=True)
                
                # Redução do Dataset
                matriculas = df.matricula.unique()
                res = pd.DataFrame()
                for matricula in matriculas:
                    res = pd.concat([res, self.__get_hospitalizacoes(matricula, df)])

                # Tempo de internação
                df['tempo_de_internacao'] = df['tempo_de_internacao'].fillna('tempo_internaao')

                # APH
                df['aph'] = df['aph'].fillna('Nao Informado').apply(lambda x: unidecode(str(x).upper().strip()))

                # Tratamento hospital
                df['hospital'] = df['hospital'].fillna('nao informado').apply(self.__hospital)
                
                # Data de alta
                df['data_alta'] = df.apply(self.__alta, axis=1)

                # Classificação de risco
                df['classificacao_de_risco'] = df['classificacao_de_risco'].fillna('ROBUSTO').apply(self.__classificacao)

                # Eletivo ou emergência
                df['eletivo_ou_emergengencia'] = df['eletivo_ou_emergengencia'].fillna(df['eletivo'])
                df['eletivo_ou_emergengencia'] = df['eletivo_ou_emergengencia'].fillna('nao informado').apply(self.__eletivo)

                # Normalização de Observação
                df['observacao'] = df['observacao'].astype(str).fillna('').apply(
                    lambda x: unidecode(x).upper().strip().replace('+',' ').replace(',', ' ').replace('.', ' ')
                )
                
                # CTI
                df['fl_cti'] = df['observacao'].astype(str).str.contains('CTI').astype(int)

                # UTI
                df['fl_uti'] = df['observacao'].astype(str).apply(lambda x: 1 if 'UTI' in x.split(' ') else 0)
                
                # Tempo de internação
                df['dias_internado'] = df.apply(self.__tempo_internacao, axis=1)
            
            with st.status('Salvando dados...'):
                postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)
            if isinstance(postgre_res, int):
                st.success('Salvo com sucesso!')
            else:
                st.error(f'Erro: {postgre_res}')
