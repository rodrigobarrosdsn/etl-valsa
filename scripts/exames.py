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

class Exames:
    def __init__(self) -> None:
        self.__table = 'tb_exames'
        self.__schema = 'valsa'
    def __normalize_str(self, txt: str) -> str:
        return unidecode(txt.upper().replace('  ', ' ').strip())

    def main(self) -> None:
        with st.container():
            ## Origens
            site_name = 'Analytics'
            folder_name = 'Dados/Dados Valsa - FRG/Exames Clinicas'

            st.html('<h1>VALSA SAÚDE</h1>')
            st.html('<h2>EXAMES E PROCEDIMENTOS</h2>')

            st.session_state.s_date = None
            st.session_state.f_date = None

            ## Carga de base
            st.session_state.s_date = st.date_input('Selecione a data inicial', format=('YYYY-MM-DD'), value=None)
            st.session_state.f_date = st.date_input('Selecione a data final', format=('YYYY-MM-DD'), value=None)

            if st.session_state.s_date and st.session_state.f_date:
                barra_local     = 'Exames_Barra.xlsx'
                copa_local      = 'Exames_Copa.xlsx'
                passos_local    = 'Exames_Passos.xlsx'
                copa2_local     = 'Exames_RJ_anterior.xlsx'

                with st.status('Processando dados da Valsa Barra...'):
                    barra = Sharepoint().get_file(barra_local, folder_name, site_name)
                with st.status('Processando dados da Valsa Passos...'):
                    passos = Sharepoint().get_file(passos_local, folder_name, site_name)
                with st.status('Processando dados da Valsa Copacabana...'):
                    copa = pd.concat([
                        Sharepoint().get_file(copa_local, folder_name, site_name),
                        Sharepoint().get_file(copa2_local, f'{folder_name}/Anterior', site_name)
                    ])
                with st.status('Obtendo dados da HealthMap...'):
                    ## Exclusão de registros nulos
                    coluna_data = 'Data Realização (dd/mm/aaaa)'
                    barra = barra[barra[coluna_data].notna()]
                    copa = copa[copa[coluna_data].notna()]
                    passos = passos[passos['Data Realização (dd/mm/aaaa)'].notna()]

                    barra.columns = [coluna.lower() for coluna in barra.columns]
                    copa.columns = [coluna.lower() for coluna in copa.columns]
                    passos.columns = [coluna.lower() for coluna in passos.columns]

                    # Seleção
                    colunas = ['data realização (dd/mm/aaaa)', 'nome beneficiário', 'carteirinha', 'idfrg', 'convênio', 
                            'código tuss exame', 'descrição código exame', 'médico solicitante', 'data da solicitação', 
                            'procedimento']
                    barra = barra[colunas]
                    copa = copa[colunas]
                    passos = passos[colunas]

                    # Identificação
                    barra['Unidade'] = 'BARRA'
                    copa['Unidade'] = 'COPACABANA'
                    passos['Unidade'] = 'PASSOS'

                    # Concatenação
                    df = pd.concat([barra, copa, passos])
                    
                    barra = copa = passos = None

                    # Tratamento de Missings
                    df['idfrg'] = df['idfrg'].fillna('0')
                    df['carteirinha'] = df['carteirinha'].fillna('0')
                    df['código tuss exame'] = df['código tuss exame'].fillna('0')
                    df['descrição código exame'] = df['descrição código exame'].fillna('Não Preenchido')

                    # Procedimento
                    df['fl_procedimento'] = df['procedimento'].apply(lambda x: x[1], axis=1)
                    df = df.drop(columns=['procedimento'])

                    # Renomeação das colunas
                    df.columns = ['data_realizacao', 'nome', 'carteirinha', 'idfrg', 'convenio', 'codigo_tuss', 
                                'descricao_exame', 'medico_solicitante', 'data_da_solicitacao', 'unidade', 'procedimento']

                    # Médico
                    df['medico_solicitante'] = df['medico_solicitante'].fillna('NAO PREENCHIDO').apply(self.__normalize_str)

                    # Tratamento de nome
                    df['nome'] = df['nome'].fillna('NAO PREENCHIDO').apply(self.__normalize_str)

                    # Tratamento descrição de exame
                    df['descricao_exame'] = df['descricao_exame'].apply(self.__normalize_str)

                    # Datas
                    def get_datas(data):
                        data = str(data).strip().split(' ')[0]
                        if data == '22/04/202':
                            data = '22/04/20223'
                        if '-' in data:
                            return datetime.fromisoformat(data)
                        else:
                            try:
                                return datetime.strptime(data, '%d/%m/%Y')
                            except:
                                return nan
                                
                    df['data_realizacao'] = df['data_realizacao'].apply(get_datas)

                    # Tratamento de Tuss
                    df['codigo_tuss'] = df['codigo_tuss'].astype(str).apply(lambda x: x.split('.')[0])

                    # Armazenamento
                    ## SQL
                    postgre_res = sgdb.postgre(df=df, table='tb_exames', schema='valsa')

                if isinstance(postgre_res, int):
                    st.success('Salve com sucesso!')
                    
                    hoje = datetime.today()
                    
                    query = f"""
                            select 
                                a.data_realizacao::date,
                                a.carteirinha,
                                a.nome,
                                b.sexo,
                                extract(year from age(b.nascimento::date)) as idade,
                                a.convenio,
                                a.codigo_tuss,
                                a.descricao_exame,
                                b.programa,
                                a.medico_solicitante,
                                a.unidade
                            from 
                                valsa.tb_exames a
                                left join valsa.tb_cadastrados_programas b on a.carteirinha = b.carteirinha::varchar
                            where
                                a.data_realizacao::date between '{st.session_state.s_date}'::date and '{st.session_state.f_date}'::date
                                and a.codigo_tuss::int > 0
                            """
                    df = sgdb.read_lakehouse(query)
                    if isinstance(df, str):
                        st.error(f'Erro: {df}')
                    else:
                        st.download_button(label='Download', data=to_excel(df), file_name=f'exames - {hoje}.xlsx')
                        st.dataframe(df)
                else:
                    st.error(f'ERRO: {postgre_res}')

        # print(f'Execução de Exames: {res}')
                    del st.session_state.s_date
                    del st.session_state.f_date

