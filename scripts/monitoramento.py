# Bibliotecas
import warnings
import pandas as pd

from unidecode import unidecode
from datetime import datetime
from numpy import inf, nan

from utils.sgdb import sgdb

warnings.filterwarnings("ignore")

class Monitoramento:
    def __init__(self) -> None:
        self.__table  : str = 'tb_monitoramento_hmap'
        self.__table_2: str = 'tb_plano_terapeutico'
        self.__schema : str = 'valsa'

    def __make_query(self) -> str:
        return 'SELECT * FROM dbo.VW_BENEFICIARIOS_1'

    def __datas(self, data: str) -> datetime:
        try:
            if '-' in data:
                return datetime.strptime(data.split(' ')[0], r'%Y-%m-%d')
            else:
                return datetime.strptime(data, r'%d/%m/%Y')
        except:
            return nan

    def __plano_terapeutico(self, df: pd.DataFrame) -> pd.Series:
        data = df['dt_vigencia']
        classificacao = df['programa']

        monitoramento: int = 0
        enfermagem: int = 0
        psicologia: int = 0
        nutricao: int = 0
        medico: int = 0

        if data.year < datetime.today().year:
            proporcao = 1
        else:
            proporcao = (365 - ((data.month -1) * 30)) / 365
            
        if classificacao == 'ROBUSTO':
            monitoramento = int(round(5 * proporcao, 0)) if 5 * proporcao > 0 else 1
            enfermagem = 1
            psicologia = 1
            nutricao = 1
        elif classificacao == 'PARCIAL':
            monitoramento = int(round(5 * proporcao, 0)) if 5 * proporcao > 0 else 1
            medico = int(round(4 * proporcao, 0)) if 4 * proporcao > 0 else 1
            enfermagem = int(round(3 * proporcao, 0)) if 3 * proporcao > 0 else 1
        else:
            monitoramento = int(round(6 * proporcao, 0)) if 6 * proporcao > 0 else 1
            medico = int(round(5 * proporcao, 0)) if 5 * proporcao > 0 else 1
            enfermagem = int(round(6 * proporcao, 0)) if 6 * proporcao > 0 else 1
            
        return pd.Series([monitoramento, enfermagem, psicologia, nutricao, medico])

    def run(self) -> tuple:
        # get dataset
        df = sgdb.mssql(self.__make_query())
        if isinstance(df, str):
            return (df, '')

        # Padronização dos nomes
        df.columns = [unidecode(coluna.lower().replace(' ', '_')) for coluna in df.columns]
        
        # Padronização do nome
        df['nome'] = df['nome'].apply(lambda x: unidecode(x.upper().strip()))
        
        # Remoção de dados de teste
        # df = df[df['nome'].str.contains('TEST').map({True: False, False: True})]
        df = df.query('~nome.str.contains("TEST")')

        # Remoção das altas
        # df = df.query('data_da_alta.isna()')

        # Seleção de beneficiários para André
        df = df.query('gestor == "Andre Luis Lopes da Silva"')
        
        # Seleção de colunas
        df = df[['carteirinha', 'nome', 'data_de_nascimento', 'sexo', 'ivcf-20', 'estado', 'data_de_admissao', 'data_da_alta']]
        
        # Novos nomes
        df.columns = ['carteirinha', 'nome', 'data_de_nascimento', 'sexo', 'programa', 'regiao', 'created_at', 'deleted_at']
      
        # Seleção dos beneficiários
        df = df.query('programa.notna()')
        
        # Tratamento de carteirinha
        # df['carteirinha'] = df['carteirinha'].fillna(0)
        
        # Tratamento de missings em região
        df['regiao'] = df['regiao'].fillna('Nao Informado')
        
        # Tratamento de sexo
        df['sexo'] = df['sexo'].str[0]
        
        # Tratamento da data de admissão
        df['created_at'] = pd.to_datetime(df['created_at'].fillna(f'1/1/{datetime.today().year}'), format='%d/%m/%Y')
        
        # Tratamento da data de nascimento
        df['data_de_nascimento'] = pd.to_datetime(df['data_de_nascimento'].fillna(f'1/1/{datetime.today().year}'), format='%d/%m/%Y')
        
        # Idade
        df['idade'] = df['data_de_nascimento'].apply(lambda dt_nasc: round((datetime.today() - dt_nasc).days / 365, 0)).astype(int)
        
        # Faixa Etária
        df['faixa_etaria'] = pd.cut(
            x = df['idade'],
            bins = [-inf, 59, 69, 79, 89, inf],
            labels = ['< 59', '60 - 69', '70 - 79', '80 - 89', '89 +']
        )
        
        # Data da vigência
        df['dt_vigencia'] = df['created_at'].apply(lambda x: x.replace(year = datetime.today().year - 1) if x.year < datetime.today().year else x)

        # Tratamento da data de exclusão
        df['deleted_at'] = pd.to_datetime(df['deleted_at'], format="%d/%m/%Y")
        
        # Tratamento da classificação de monitoramento
        df['programa'] = df['programa'].apply(lambda x: unidecode(x.upper()))
        df['programa'] = df['programa'].str.replace('POTENCIALMENTE FRAGIL', 'PARCIAL')

        # Plano terapêutico
        df[['monitoramento', 'enfermagem', 'psicologia', 'nutricao', 'medico']] = df.apply(self.__plano_terapeutico, axis=1)

        # Therapeutic data
        colunas_terapeutico = ['created_at', 'carteirinha', 'nome', 'programa', 'regiao', 'dt_vigencia', 'monitoramento', 'enfermagem', 'psicologia', 'nutricao', 'medico']
        
        colunas_monitoramento = ['created_at', 'deleted_at', 'carteirinha', 'nome', 'sexo', 'data_de_nascimento', 
                                 'idade', 'faixa_etaria', 'programa', 'regiao']

        # Remoção de duplicatas
        df = df.drop_duplicates()
        
        # make response
        monitoramento_res   = dict()
        terapeutico_res     = dict()

        ## monitoramento
        postgre_res = sgdb.postgre(df=df[colunas_monitoramento], table=self.__table, schema=self.__schema)
        if isinstance(postgre_res, int):
            monitoramento_res['msg'] = postgre_res
        else:
            monitoramento_res['error'] = postgre_res

        ## plano terapeutico
        postgre_res = sgdb.postgre(df=df[colunas_terapeutico], table=self.__table_2, schema=self.__schema)

        if isinstance(postgre_res, int):
            terapeutico_res['msg'] = postgre_res
        else:
            terapeutico_res['error'] = postgre_res

        return monitoramento_res, terapeutico_res

def main():
    monitoramento = Monitoramento()
    monitoramento_res, terapeutico_res = monitoramento.run()

    print(f'Execução de Monitoramento: {monitoramento_res}')
    print(f'Execução de Plano Terapêutico: {terapeutico_res}')

main()
