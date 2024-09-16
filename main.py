import streamlit as st
from streamlit_option_menu import option_menu

from scripts.sql import SQL
from scripts.exames import Exames
from scripts.obitos import Obitos
from scripts.ligacoes import Ligacoes
from scripts.dashboards import Dashboards
from scripts.agendamentos import Agendamentos
from scripts.beneficiarios import Beneficiarios
from scripts.hospitalizacao import Hospitalizacao
from scripts.cadastrados_programas import CadastradosProgramas

st.set_page_config(layout="wide")
with st.sidebar:
    selected = option_menu(
        menu_title='MENU',
        options=[
            'Início',
            'Exames',
            'Agendamento',
            'Beneficiário xlsx',
            'Beneficiários hmap',
            'Atualização - Melhor Idade',
            'SQL'
        ],
        menu_icon='cast',
        # orientation='horizontal',
        default_index=0
    )

if selected == 'Início':
    Dashboards().run()

elif selected == 'Beneficiários hmap':
    Beneficiarios().run()

elif selected == 'Exames':
    Exames().main()

elif selected == 'Agendamento':
    Agendamentos().main()

elif selected == 'Beneficiário xlsx':
    CadastradosProgramas().main()

elif selected == 'Atualização - Melhor Idade':
    try:
        Ligacoes().run()
    except Exception as e:
        st.error(f'Erro: {e}')
    try:
        Obitos().run([2023, 2024])
    except Exception as e:
        st.error(f'Erro: {e}')
    try:
        Hospitalizacao().run([2023, 2024])
    except Exception as e:
        st.error(f'Erro: {e}')

elif selected == 'SQL':
    SQL().main()
