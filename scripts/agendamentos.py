
Editar
Nenhuma linha está selecionada.
# Bibliotecas
import warnings
import streamlit as st

from pandas import DataFrame
from unidecode import unidecode
from datetime import datetime

from utils.sgdb import SGDB
from utils.files import to_excel

warnings.filterwarnings("ignore")


class Agendamentos:
    def __init__(self) -> None:
        self.__table = 'tb_consultas'
        self.__schema = 'valsa'
    def __valida_especialidade(self, especialidade: str) -> int:
        lista_especialidades = ['ENDOCRINOLOGISTA', 'PSICOLOGA', 'NUTRICIONISTA', 'GERIATRIA',
                                'CARDIOLOGISTA', 'DERMATOLOGISTA', 'GINECOLOGISTA', 'PSIQUIATRA',
                                'FISIOTERAPEUTA', 'ORTOPEDISTA']
        return 1 if especialidade in lista_especialidades else 0

    def __valida_encaminhamento(self, encaminhamento: str) -> int:
        return 0 if encaminhamento == 'NAO INFORMADO' else 1

    def main(self) -> DataFrame:
        with st.container():

            if st.button('Carregar'):
                query = """
                SELECT
                    ag.codigo_consulta,
                    ag.dt_consulta,
                    ag.dt_realizacao,
                    ag.cpf,
                    CASE
                        WHEN ag.carteirinha IS NULL THEN '-1'
                        ELSE ag.carteirinha
                    END as carteirinha,
                    ag.sexo,
                    ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) as idade,
                    CASE 
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) < 19 THEN '00-18'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 19 AND 23 THEN '19-23'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 24 AND 28 THEN '24-28'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 29 AND 33 THEN '29-33'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 34 AND 38 THEN '34-38'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 39 AND 43 THEN '39-43'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 44 AND 48 THEN '44-48'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 49 AND 53 THEN '49-53'
                        WHEN ROUND(DATEDIFF(DD, ag.dt_nascimento, ag.dt_consulta) / 365.25, 0) BETWEEN 54 AND 58 THEN '54-58'
                        ELSE '59+'
                    END as faixa_etaria,
                    ag.profissional,
                    CASE
                        WHEN ag.especialidade LIKE '%CARDIO%' THEN 'CARDIOLOGISTA'
                        WHEN ag.especialidade LIKE '%DERMATO%' THEN 'DERMATOLOGISTA'
                        WHEN ag.especialidade LIKE '%ENDOCRIN%' THEN 'ENDOCRINOLOGISTA'
                        WHEN ag.especialidade LIKE '%GERAL%' THEN 'CLINICO'
                        WHEN ag.especialidade LIKE '%CLINIC%' THEN 'CLINICO'
                        WHEN ag.especialidade LIKE '%FISIOT%' THEN 'FISIOTERAPEUTA'
                        WHEN ag.especialidade LIKE '%GERIATR' THEN 'GERIATRA'
                        WHEN ag.especialidade LIKE '%ORTOP%' THEN 'ORTOPEDISTA'
                        WHEN ag.especialidade LIKE '%PSIQUIA%' THEN 'PSIQUIATRA'
                        WHEN ag.especialidade LIKE '%NUTRI%' THEN 'NUTRICIONISTA'
                        WHEN ag.especialidade LIKE '%ENFERM%' THEN 'ENFERMEIRO'
                        WHEN ag.especialidade LIKE '%GINECO%' THEN 'GINECOLOGISTA'
                        WHEN ag.especialidade LIKE '%OBSTETR%' THEN 'GINECOLOGISTA'
                        ELSE ag.especialidade
                    END as especialidade,
                    CASE
                        WHEN ag.gestor IS NULL THEN 'NAO INFORMADO'
                        ELSE ag.gestor
                    END as gestor,
                    CASE 
                        WHEN ag.status_consulta IS NULL THEN 'NAO INFORMADO'
                        ELSE ag.status_consulta
                    END as status_consulta,
                    CASE
                        WHEN ag.unidade_atendimento LIKE '%COPACABANA%' THEN 'COPACABANA'
                        WHEN ag.unidade_atendimento LIKE '%BARRA%' THEN 'BARRA'
                        WHEN ag.unidade_atendimento LIKE '%PASSOS%' THEN 'PASSOS'
                        WHEN ag.unidade_atendimento LIKE '%MONITORAMENTO%' THEN 'MONITORAMENTO'
                        ELSE 'OUTROS'
                    END as unidade_atendimento,
                    CASE
                        WHEN ag.tipo IS NULL THEN 'NAO INFORMADO'
                        ELSE ag.tipo
                    END AS tipo,
                    CASE 
                        WHEN ag.encaminhamento_especialidade IS NULL THEN 'NAO INFORMADO'
                        ELSE ag.encaminhamento_especialidade
                    END as encaminhamento_especialidade
                FROM
                    (
                        SELECT
                            [CÓDIGO CONSULTA] as codigo_consulta,
                            [DATA DA CONSULTA] as dt_consulta,
                            [DATA DA REALIZAÇÃO] as dt_realizacao,
                            CONVERT(DATETIME, [DATA DE NASCIMENTO], 103) as dt_nascimento,
                            [CPF] as cpf,
                            [CARTEIRINHA] as carteirinha,
                            UPPER([SEXO]) as sexo,
                            UPPER([PROFISSIONAL]) as profissional,
                            UPPER([ESPECIALIDADE]) as especialidade,
                            UPPER([GESTOR]) as gestor,
                            UPPER([STATUS CONSULTA]) as status_consulta,
                            UPPER([UNIDADADE CONSULTA]) as unidade_atendimento,
                            UPPER([TIPO]) as tipo,
                            UPPER([ENCAMINHAMENTO (ESPECIALIDADE)]) as encaminhamento_especialidade
                        FROM
                            dbo.VW_RELATORIO_PEP
                        WHERE 
                            LOWER([UNIDADADE CONSULTA]) LIKE '%valsa%'
                    ) ag;
                """

                with st.status('Carregando dados do Healthmap...'):
                    df = SGDB().mssql_pep(query)

        
                df['profissional'] = df['profissional'].apply(unidecode)
                df['especialidade'] = df['especialidade'].apply(unidecode)
                df['gestor'] = df['gestor'].apply(unidecode)
                df['encaminhamento_especialidade'] = df['encaminhamento_especialidade'].apply(unidecode)

                df['sexo'] = df['sexo'].str[0]

                df['fl_especialista'] = df['especialidade'].apply(self.__valida_especialidade)
                df['fl_encaminhamento'] = df['encaminhamento_especialidade'].apply(self.__valida_encaminhamento)

                df['idade'] = df['idade'].astype(int)
                

                df = df.drop_duplicates()

                with st.status('Processando os dados...'):
                    postgre_res = SGDB().postgre(df=df, table=self.__table, schema=self.__schema)
                if isinstance(postgre_res, int):
                    st.success('Processado com sucesso!')
                else:
                    st.error(f'Erro: {postgre_res}')

                saida = df.query(f'"{st.session_state.s_date}" <= dt_consulta <= "{st.session_state.f_date}"')
                st.download_button(label='Download', data=to_excel(saida), file_name=f'exames - {datetime.today()}.xlsx')
                st.dataframe(saida)
