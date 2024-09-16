import warnings
import pandas as pd

from sqlalchemy import create_engine
from unidecode import unidecode

from utils.sharepoint import Monitoramento as SharePoint
from utils.sgdb import sgdb

warnings.simplefilter('ignore')

class Produtividade:
    def __init__(self) -> None:
        self.__table  : str = 'tb_controle_produtividade'
        self.__schema : str = 'valsa'

    def __make_query(self) -> pd.DataFrame:
        site_name = 'monitoramento'
        folder_name_rj_2024 = "RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - RJ"
        folder_name_mg_2024 = "RJ - Melhor Idade/PLANILHA VALSA/PLANILHAS VALSA 2024/PLANILHAS VALSA 2024 - MG"

        file_name_2024_mg = "Controle diário de Produtividade - Passos MG - 2024.xlsx"
        file_name_2024_rj = "Controle diário de Produtividade - Rio de Janeiro - 2024.xlsx"

        sheet_names = ('JAN - 2024', 'FEV - 2024', 'MAR - 2024', 'ABR - 2024',
                       'MAI - 2024', 'JUN - 2024', 'JUL - 2024', 'AGO - 2024',
                       'SET - 2024', 'OUT - 2024', 'NOV - 2024', 'DEZ - 2024')
        
        mes_dict = {
                    'JAN': '01', 'FEV': '02', 'MAR': '03',
                    'ABR': '04', 'MAI': '05', 'JUN': '06',
                    'JUL': '07', 'AGO': '08', 'SET': '09',
                    'OUT': '10', 'NOV': '11', 'DEZ': '12' 
                    }

        df = pd.DataFrame()
        for sheet_name in sheet_names:
            # RJ 2024
            temp = SharePoint().ligacoes(file_name_2024_rj, folder_name_rj_2024, 
                                         site_name, sheet_name=sheet_name, skiprows=2)
            
            temp.rename(columns={'Dia do mês': 'dia_do_mes'}, inplace=True)
            temp = temp.query('dia_do_mes.notna()')
            temp = temp[[column for column in temp.columns if not 'named' in str(column)]]
            temp.set_index('dia_do_mes', inplace=True)
            temp = temp.T
            temp.columns = [unidecode(column).lower().replace('  ', '').replace('/', ' ').replace('  ', '').replace(' ', '_') for column in temp.columns]
            temp = temp.reset_index().rename(columns={'index': 'dia_do_mes'})

            temp['dia_do_mes'] = temp['dia_do_mes'].apply(lambda x: f'2024-{mes_dict.get(sheet_name.split(" ")[0][:3])}-{x}').astype('datetime64[ns]')
            temp['uf'] = 'RJ'
            df = pd.concat([df, temp])

            # MG 2024
            temp = SharePoint().ligacoes(file_name_2024_mg, folder_name_mg_2024, 
                                         site_name, sheet_name=sheet_name, skiprows=1)

            temp.rename(columns={'Dia do mês': 'dia_do_mes'}, inplace=True)
            temp = temp.query('dia_do_mes.notna()')
            temp = temp[[column for column in temp.columns if not 'named' in str(column)]]
            temp.set_index('dia_do_mes', inplace=True)
            temp = temp.T
            temp.columns = [unidecode(column).lower().replace('  ', '').replace('/', ' ').replace('  ', '').replace(' ', '_') for column in temp.columns]
            temp = temp.reset_index().rename(columns={'index': 'dia_do_mes'})

            temp['dia_do_mes'] = temp['dia_do_mes'].apply(lambda x: f'2024-{mes_dict.get(sheet_name.split(" ")[0][:3])}-{x}').astype('datetime64[ns]')
            temp['uf'] = 'MG'
            df = pd.concat([df, temp])

        return df

    def __to_int(self, x: int) -> int:
        try:
            return int(x)
        except:
            return 0
        
    def run(self):
        # Leitura do dataset
        df = self.__make_query()

        # Conversão para Inteiro
        colunas_numericas = df.drop(columns=['tipo_atendimento', 'uf']).columns
        for coluna in colunas_numericas:
            df[coluna] = df[coluna].apply(self.__to_int)
        
        # Soma de atendimentos
        colunas_nao_numericas = ['tipo_atendimento', 'mes_safra', 'ano_safra', 'uf']
        df['total_atendimentos'] = df.drop(columns=colunas_nao_numericas).sum(axis=1)

        # Seleção de colunas
        df = df[['tipo_atendimento', 'total_atendimentos', 'mes_safra', 'ano_safra', 'uf']]
        
        postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)

        if isinstance(postgre_res, int):
            return {'msg': postgre_res}
        else:
            return {'error': postgre_res}

def main():
    produtividade = Produtividade()
    res = produtividade.run()

    print(f'Execução de Óbitos: {res}')

main()
