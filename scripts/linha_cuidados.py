# Bibliotecas
import warnings
import pandas as pd

from unidecode import unidecode
from datetime import datetime
from numpy import inf, nan

from utils.sgdb import sgdb
from utils.sharepoint import Analytics as SharePoint

warnings.filterwarnings("ignore")

class Monitoramento:
    def __init__(self) -> None:
        self.__table  : str = 'tb_linha_cuidados'
        self.__schema : str = 'valsa'

    def __make_query(self) -> pd.DataFrame:
        site_name='analytics'
        folder_name = 'Dados/Dados Valsa - FRG/Programas'
        file_name = 'Cadastrados Programas.xlsx'
        sheet_name = 'Dados'
        return SharePoint().linha_cuidados(file_name, folder_name, site_name, sheet_name=sheet_name)
    
    def __tempo_para_maior_idade(self, nascimento: datetime) -> int:
        hoje = datetime.today()
        dias = (nascimento - datetime(hoje.year-59,hoje.month,hoje.day)).days
        return dias

    def __datas(self, data: str) -> datetime:
        try:
            if '-' in data:
                return datetime.strptime(data.split(' ')[0], r'%Y-%m-%d')
            else:
                return datetime.strptime(data, r'%d/%m/%Y')
        except:
            return nan

    def run(self) -> tuple:
        # get dataset
        df = self.__make_query()
        
        # Normalização dos nomes
        df.columns = [unidecode(coluna).lower().strip().replace(' ', '_') for coluna in df.columns]

        # Normalização de programa
        df['programa'] = df['programa'].fillna('nao informado').apply(lambda x: unidecode(x).upper())
        
        # Idade
        df['idade'] = df['nascimento'].apply(lambda x: (datetime.today() - x).days / 365).round(0).fillna(-1).astype(int)

        # Faixa Etaria
        x = df['idade']
        bins = [-inf, 18, 23, 28, 33, 38, 43, 48, 53, 58, inf]
        labels = ['00 - 18', '19 - 23', '24 - 28', '29 - 33', '34 - 38', '39 - 43', '44 - 48', '49 - 53', '54 - 58', '59 +']

        df['faixa_etaria'] = pd.cut(x=x, bins=bins, labels=labels)
        
        # Flag 59 anos
        df['dias_melhor_idade'] = df['nascimento'].apply(self.__tempo_para_maior_idade)

        # Seleção dos beneficiários
        df = df.query('programa.str.contains("PASSOS") & (14 <= idade <= 58 & tipo_adesao_clinica_passos == "Presencial")')
        
        # IDFRG
        df['id_frg'] = df['id_frg'].fillna(0).astype(int)

        # Seleção
        df = df[['id_frg', 'carteirinha', 'nascimento', 'idade', 'faixa_etaria', 'dias_melhor_idade', 'sexo', 'data_de_adesao', 'tipo_adesao_clinica_passos']]

        # Carteirinha
        df['carteirinha'] = df['carteirinha'].apply(lambda x: int(x))

        ## Salvando
        postgre_res = sgdb.postgre(df=df, table=self.__table, schema=self.__schema)
        if isinstance(postgre_res, int):
            return {'msg': postgre_res}
        else:
            return {'error': postgre_res}

def main():
    m = Monitoramento()
    res = m.run()
    print(f'Execução de Linha de Cuidados: {res}')

main()
