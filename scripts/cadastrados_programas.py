## Bibliotecas
import warnings
import pandas as pd
import streamlit as st

from numpy import nan
from datetime import datetime
from unidecode import unidecode
warnings.filterwarnings('ignore')
## Funções e Configurações

from utils.sharepoint import Analytics as Sharepoint
from utils.files import to_excel
from utils.sgdb import sgdb

class CadastradosProgramas:
    def __init__(self) -> None:
        self.__table = 'tb_cadastrados_programas'
        self.__schema = 'valsa'

    def __normalize_str(self, txt: str) -> str:
        return unidecode(txt.upper().replace('  ', ' ').strip())
    
    def __get_ddd(self, x: pd.DataFrame) -> str:
         ddd = x.ddd_celular if str(x.ddd) == '0' else x.ddd
         return str(ddd).split('.')[0]

    def __concat_telefones(self, x: pd.DataFrame) -> str:
        res = None
        if str(x.telefones) != '0':
            res = str(x.telefones)
        if str(x.celular) != '0':
            if res:
                res = f'{res} | {str(x.celular)}'
            else:
                res = str(x.celular)
        return res
    
    def __concat_emails(self, x: pd.DataFrame) -> str:
        email = str(x.email_1).lower() if str(x.email_1) != '0' else 'nao cadastrado'
        if str(x.email_2) != '0':
              email = f'{email} | {str(x.email_2).lower()}'
        return email
    
    def __to_int(self, x: str) -> str:
        try:
            return str(int(x))
        except:
            return str(0)

    def main(self) -> None:
            ## Origens
            site_name = 'Analytics'
            folder_name = 'Dados/Dados Valsa - FRG/Programas'

            st.html('<h1>VALSA SAÚDE</h1>')
            st.html('<h2>CADASTRADOS NOS PROGRAMAS</h2>')

            file_name = 'Cadastrados Programas.xlsx'
            sheet_name = 'Dados'
            type_read = 'dataframe'

            with st.status('Carregando a tabela...'):
                df = Sharepoint().get_file(file_name, folder_name, site_name, type_read, sheet_name)

            df.columns = [
                        'nome', 'id_frg', 'sexo', 'nascimento', 'idade', 'ddd', 'telefones',
                        'ddd_celular', 'celular', 'email_1', 'email_2', 'carteirinha',
                        'programa', 'uf', 'tipo_adesao_clinica_passos', 'dt_adesao', 'dt_exclusao',
                        'notivo_exclusao', 'telefone_atual', 'email_atual'
                        ]

            with st.status('Processando a tabela ...'):
                df = df.query('nome.notna()')

                df['nome'] = df['nome'].apply(self.__normalize_str)
                df['id_frg'] = df['id_frg'].fillna('nao informado').astype(str).apply(lambda x: self.__normalize_str(x).replace(',', '').split('.')[0])
                df['carteirinha'] = df['carteirinha'].fillna('0').apply(self.__to_int)

                df['ddd'] = df.apply(self.__get_ddd, axis=1)
                df['telefones'] = df.fillna('0').apply(self.__concat_telefones, axis=1).fillna('nao informado')
                df['email'] = df.fillna('0').apply(self.__concat_emails, axis=1)


            
                df = df.drop(columns=['ddd_celular', 'celular', 'email_1', 'email_2', 'idade'])

            with st.status('Salvando cópia de segurança...'):
                res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)

            if isinstance(res, int):
                st.success('Salvo com sucesso!')
            else:
                st.error(f'Erro: {res}')
            
            st.dataframe(df)
