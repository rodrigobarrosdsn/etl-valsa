## Bibliotecas
import warnings
import streamlit as st

from pandas import DataFrame
from unidecode import unidecode
from datetime import datetime

from utils.sgdb import SGDB
from utils.files import to_excel

warnings.filterwarnings('ignore')

class Beneficiarios:
    def __init__(self) -> None:
        self.__table = 'tb_beneficiarios'
        self.__schema = 'valsa'

    def __trata_string(self, x: str) -> str:
        return unidecode(x).strip()

    def __get_endereco(self, x: DataFrame) -> str:
        rua = x.endereco if isinstance(x.endereco, str) else ''
        bairro = x.bairro if isinstance(x.bairro, str) else ''
        cidade = x.cidade if isinstance(x.cidade, str) else ''
        uf = x.uf if isinstance(x.uf, str) else ''
        return f'{rua}, {bairro}, {cidade}, {uf}, BR'

    def run(self) -> None:
        with st.container():
            st.html('<h1>VALSA SAÚDE</h1>')
            st.html('<h1>BENEFICIÁRIOS</h1>')
            query = """
                    select
                        b.carteirinha,
                        CASE
                            WHEN b.convenio IS NULL THEN 'NAO PREENCHIDO'
                            ELSE b.convenio
                        END as convenio,
                        b.nome,
                        b.sexo,
                        b.email,
                        b.telefone,
                        b.cpf,
                        b.dt_nascimento,
                        ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) as idade,
                        CASE 
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) < 19 THEN '00-18'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 19 AND 23 THEN '19-23'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 24 AND 28 THEN '24-28'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 29 AND 33 THEN '29-33'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 34 AND 38 THEN '34-38'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 39 AND 43 THEN '39-43'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 44 AND 48 THEN '44-48'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 49 AND 53 THEN '49-53'
                            WHEN ROUND(DATEDIFF(DD, b.dt_nascimento, GETDATE()) / 365.25, 0) BETWEEN 54 AND 58 THEN '54-58'
                            ELSE '59+'
                        END as faixa_etaria,
                        b.endereco,
                        b.bairro,
                        b.cidade,
                        b.uf,
                        CASE
                            WHEN b.gestor IS NULL THEN 'SEM GESTOR'
                            ELSE b.gestor
                        END as gestor,
                        CASE
                            WHEN b.classificacao IS NULL THEN 'SEM CLASSIFICACAO'
                            WHEN b.classificacao = 'POTENCIALMENTE FRÁGIL' THEN 'PARCIAL'
                            ELSE b.classificacao
                        END as classificacao,
                        b.dt_admissao,
                        b.dt_alta
                    from
                        (
                        select 
                            UPPER([NOME]) as nome,
                            [CPF] as cpf,
                            [CARTEIRINHA] as carteirinha,
                            UPPER([SEXO]) as sexo,
                            LOWER([EMAIL]) as email,
                            [CELULAR] as telefone,
                            UPPER([ENDEREÇO]) as endereco,
                            UPPER([BAIRRO]) as bairro,
                            UPPER([CIDADE]) as cidade,
                            UPPER([ESTADO]) as uf,
                            UPPER([GESTOR]) as gestor,
                            UPPER([IVCF-20]) as classificacao,
                            CONVERT(DATE, [DATA DE ADMISSÃO], 103) as dt_admissao,
                            CONVERT(DATE, [DATA DA ALTA], 103) as dt_alta,
                            CONVERT(DATETIME, [DATA DE NASCIMENTO], 103) AS dt_nascimento,
                            UPPER([CONVÊNIO]) as convenio
                        from 
                            P_HEALTHMAP_CLINICADOC.dbo.VW_BENEFICIARIOS_1
                        where 
                            UPPER([NOME]) NOT LIKE '%TEST%'
                            AND [CARTEIRINHA] IS NOT NULL
                        ) b;
                        """ 
            with st.status('Carregando os Dados dos Beneficiários HealthMap...'):
                df = SGDB().mssql(query)
                st.write(df)

            df['nome'] = df['nome'].apply(self.__trata_string)
            df['gestor'] = df['gestor'].apply(self.__trata_string)
            df['classificacao'] = df['classificacao'].apply(self.__trata_string)
            df['endereco_completo'] = df.apply(self.__get_endereco, axis=1)

            # df['carteirinha'] = df['carteirinha'].fillna('-1').astype(float)

            df = df.drop_duplicates()
            
            with st.status('Salvando os dados dos Beneficiários no banco de dados Grupo Valsa...'):
                res = SGDB().postgre(df, self.__table, self.__schema)

            if isinstance(res, int):
                st.success('Salvo com sucesso!')
                
                hoje = datetime.now()
                st.download_button(label='Download', data=to_excel(df), file_name=f'exames - {hoje}.xlsx')
                st.dataframe(df)
            else:
                st.error(f'ERRO: {res}')
