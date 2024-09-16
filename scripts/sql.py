import warnings
import streamlit as st

from datetime import datetime

from utils.sgdb import SGDB
from utils.files import to_excel

warnings.filterwarnings("ignore")

class SQL:
    def main(self):
        query = st.text_area('Código SQL')

        banco = st.selectbox('Banco de dados alvo', ('healthmap', 'healthmap pep'))

        if st.button('Executar'):
            with st.status('Carregando...'):
                if banco == 'healthmap':
                    df = SGDB().mssql(query)
                elif banco == 'healthmap pep':
                    df = SGDB().mssql_pep(query)
                
            st.download_button(label='Download', data=to_excel(df), file_name=f'{banco} - {datetime.today()}.xlsx')
            st.dataframe(df)
