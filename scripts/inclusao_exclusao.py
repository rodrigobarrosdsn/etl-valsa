import pandas as pd
from unidecode import unidecode
from datetime import datetime

from utils.sharepoint import Monitoramento as SharePoint
from utils.sgdb import sgdb

class InclusaoExclusao:
    def __init__(self) -> None:
        self.__table = 'tb_inclusao_exclusao'
        self.__schema = 'valsa'

    def main(self) -> None:
        site_name='monitoramento'

        mes_dict = {
            'JAN': '01', 'FEV': '02', 'MAR': '03',
            'ABR': '04', 'MAI': '05', 'JUN': '06',
            'JUL': '07', 'AGO': '08', 'SET': '09',
            'OUT': '10', 'NOV': '11', 'DEZ': '12' 
        }

        folder_name = 'RJ - Melhor Idade\PLANILHA VALSA\PLANILHAS VALSA 2024\PLANILHAS VALSA 2024 - RJ\INCLUSÃO E  EXCLUSÃO 2024'
        file_names = ('ABRIL 2024.xlsx', 'AGOSTO 2024.xlsx', 'DEZEMBRO 2024.xlsx', 'FEVEREIRO 2024.xlsx', 'JANEIRO 2024.xlsx',
                      'JULHO 2024.xlsx', 'JUNHO 2024.xlsx', 'MAIO 2024.xlsx', 'MARÇO 2024.xlsx', 'NOVEMBRO 2024.xlsx',
                      'OUTUBRO 2024.xlsx', 'SETEMBRO 2024.xlsx')
        
        df = pd.DataFrame()
        for file_name in file_names:
        
            temp = SharePoint().get_file(file_name, folder_name, site_name)
            ano_mes = file_name.split(' ')

            ano = ano_mes[1].split('.')[0]
            mes = mes_dict.get(ano_mes[0][:3])

            temp['safra'] = datetime(year=int(ano), month=int(mes), day=1)
                
            df = pd.concat([df, temp])

        df = df.rename(columns={'Unnamed: 9': 'STATUS'})
        df.columns = [unidecode(coluna).lower() for coluna in df.columns]

        df['alteracao'] = df['solicitacao'].isna().map({True: 'Exclusao', False: 'Inclusao'})
        df['status'] = df['status'].fillna('nao informado')

        # Armazenamento
        ## SQL
        postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)

        if isinstance(postgre_res, int):
            res = {'msg': postgre_res}
        else:
            res = {'error': postgre_res}

        print(f'Execução de Inclusao e Exclusao: {res}')

def main():
    ie = InclusaoExclusao()
    ie.main()

main()
