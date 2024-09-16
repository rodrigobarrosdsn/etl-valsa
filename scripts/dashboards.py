import streamlit as st
import pandas as pd

class Dashboards:
    def __init__(self) -> None:
        self.monitoramento_manutencao = 'https://app.powerbi.com/groups/769dbee8-b612-46f2-a2e2-bc2a9e1d97be/reports/8407959d-59e7-4bb3-b990-f2e5b24c343c/1efa191c2bb9b0b95cda?experience=power-bi'
        self.monitoramento_web = 'https://app.powerbi.com/view?r=eyJrIjoiZjgzNWEyNTEtNTExOS00ZTM3LWExMmMtNDI5N2E1ZjlhZTg4IiwidCI6IjZmOWM2Y2Q0LWFkOGQtNGE1Yy04NWE3LTliNTQxYmQyN2RhNCJ9'

        self.satisfacao_manutencao = 'https://app.powerbi.com/groups/769dbee8-b612-46f2-a2e2-bc2a9e1d97be/reports/ba1da5d1-5977-4557-941d-75ba1a7a1ee0/52bd01a32c363aaf486c?experience=power-bi'
        self.satisfacao_web = 'https://app.powerbi.com/view?r=eyJrIjoiODVhMjI3ZGUtZWM1Zi00NDUwLWEwNTEtYmU2MWI3ZmYxYzZhIiwidCI6IjZmOWM2Y2Q0LWFkOGQtNGE1Yy04NWE3LTliNTQxYmQyN2RhNCJ9'

        self.clinicas_manutencao = 'https://app.powerbi.com/groups/7f73eedf-0d14-45f0-bd4e-9e8e222c9e44/reports/8ca226fa-dac4-4d58-84ed-12318adb6acd/ReportSection0d69336987abd6516460?experience=power-bi'
        self.clinicas_web = 'https://app.powerbi.com/view?r=eyJrIjoiMmY0MzlkMjAtOTBkYy00NjI2LWFlMDEtODAzMjIxYWVmZWZmIiwidCI6IjZmOWM2Y2Q0LWFkOGQtNGE1Yy04NWE3LTliNTQxYmQyN2RhNCJ9'

        self.mapa_manutencao = 'https://app.powerbi.com/groups/769dbee8-b612-46f2-a2e2-bc2a9e1d97be/reports/a21bc004-9329-4c80-9c26-4e7638d3c9c3/ReportSection?experience=power-bi'
        self.mapa_web = 'https://app.powerbi.com/view?r=eyJrIjoiZTRlYzE3YzMtZWYwZC00ODQ3LTg3ODItMmNjYTAzNjJkZTFiIiwidCI6IjZmOWM2Y2Q0LWFkOGQtNGE1Yy04NWE3LTliNTQxYmQyN2RhNCJ9'

    def run(self) -> None:
        with st.container():
            st.html('<h1>VALSA SAÚDE</h1>')

            # MONITORAMENTO MELHOR IDADE - VALSA
            st.divider()
            st.html('<h2>MONITORAMENTO MELHOR IDADE</h2>')
            st.write('Links')
            col1, col2 = st.columns(2)
            with col1:
                st.link_button('Relatório Web', self.monitoramento_web)
           
            with col2:
                st.link_button('Manutenção PBI', self.monitoramento_manutencao)
            
            columns = ('Tabela - Lakehouse',
                       'Tabela - Origem',
                       'Fonte - Origem',
                       'Frequência de Atualização')
            data = (
                (
                    'tb_beneficiarios',
                    'P_HEALTHMAP_CLINICADOC.dbo.VW_BENEFICIARIOS_1',
                    'Healthmap',
                    'Semanal'
                ),
                (
                     'tb_hospitalizacao',
                     'CONTROLE DE HOSPITALIZAÇÃO 2024.xlsx | HOSPITALIZADOS.xlsx',
                     'Sharepoint',
                     'Semanal'
                ),
                (
                      'tb_ligacoes_externas',
                      'LIGAÇOES EXTERNAS 2023.xlsx | LIGAÇOES EXTERNAS 2024.xlsx',
                      'Sharepoint',
                      'Semanal'
                ),
                (
                     'tb_obitos',
                     'PLANILHA DE OBITO 2024.xlsx',
                     'Sharepoint',
                     'Semanal'
                )
            )

            st.html('<br><br>')
            st.write('Documentação')
            st.table(pd.DataFrame(data, columns=columns))

            # PESQUISA DE SATISFAÇÃO - VALSA
            st.divider()
            st.html('<h2>PESQUISA DE SATISFAÇÃO</h2>')

            st.html('<br><br>')
            st.write('Links')
            col1, col2 = st.columns(2)
            with col1:
                st.link_button('Relatório Web', self.satisfacao_web)
            with col2:
                st.link_button('Manutenção PBI', self.satisfacao_manutencao)

            st.html('<br><br>')

            columns = ('Origem', 'Frequência de Atualização')
            data = (
                ('Pesquisa de Satisfação - Barra', 'Semanal'),
                ('Pesquisa de Satisfação - Copacabana', 'Semanal'),
                ('Pesquisa de Satisfação - Passos', 'Semanal'),
                ('Pesquisa de Satisfação - Monitoramento', 'Semanal')
            )

            st.write('Documentação')
            st.table(pd.DataFrame(data, columns=columns))

            # CLÍNICAS - VALSA
            st.divider()
            st.html('<h2>CLÍNICAS VALSA</h2>')
            st.warning('ESSE RELATÓRIO ENCONTRA-SE EM MANUTENÇÃO', icon="⚠️")

            st.html('<br><br>')
            st.write('Links')
            col1, col2 = st.columns(2)
            with col1:
                st.link_button('Relatório Web', self.clinicas_web)
            with col2:
                st.link_button('Manutenção PBI', self.clinicas_manutencao)

            columns = (
                'Tabela - Lakehouse',
                'Tabela - Origem',
                'Fonte - Origem',
                'Frequência de Atualização'
            )

            data = (
                ('tb_beneficiarios', 'P_HEALTHMAP_CLINICADOC.dbo.VW_BENEFICIARIOS_1', 'Healthmap', 'Semanal'),
                ('tb_consultas', 'dbo.VW_RELATORIO_PEP', 'Healthmap PEP', 'Semanal')
            )

            st.html('<br><br>')
            st.write('Documentação')
            st.table(pd.DataFrame(data, columns=columns))

            # MAPA DO MONITORAMENTO
            st.divider()
            st.html('<h2>MAPA DO MONITORAMENTO</h2>')
            st.warning('ESSE RELATÓRIO ENCONTRA-SE EM MANUTENÇÃO', icon="⚠")

            st.html('<br><br>')
            st.write('Links')
            col1, col2 = st.columns(2)
            with col1:
                st.link_button('Relatório Web', self.mapa_web)
            with col2:
                st.link_button('Manutenção PBI', self.mapa_manutencao)

            columns = (
                    'Tabela - Lakehouse',
                    'Tabela - Origem',
                    'Fonte - Origem',
                    'Frequência de Atualização'
            )

            data = (
                    ('tb_beneficiarios', 'P_HEALTHMAP_CLINICADOC.dbo.VW_BENEFICIARIOS_1', 'Healthmap', 'Semanal'),
            )

            st.html('<br><br>')
            st.write('Documentação')
            st.table(pd.DataFrame(data, columns=columns))
