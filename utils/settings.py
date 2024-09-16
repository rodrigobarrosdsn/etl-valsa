class Settings:
    def __init__(self):
        # DATA LAKE -> POSTGRE
        self.DL_HOST                = 'pg-datalake.cxrwm6vnh0nz.sa-east-1.rds.amazonaws.com'
        self.DL_USER                = 'analytics'
        self.DL_PWD                 = '.JCBD_v6RmZa-LMXLw9ek4LQm7W'
        self.DL_DATABASE            = 'postgres'

        # HMAP SGDB
        self.HMAP_USER              = "p_healthmap_clinicadoc_view"
        self.HMAP_HOST              = "119.8.155.38"
        self.HMAP_PWD               = "5InK@2t3E|Z_2RJo"
        self.HMAP_DATABASE          = "P_HEALTHMAP_CLINICADOC"

        # HMAP SGDB 2
        self.HMAP_USER_PEP          = "p_clinicadoc_view_vw_relatorio_pep"
        self.HMAP_PWD_PEP           = "(%z8!W/\\aD7036h]"
        self.MS_ODBC                = "FreeTDS"

        # SHAREPOINT VALSA
        self.SHAREPOINT_EMAIL       = 'analytics@grupovalsa.com.br'
        self.SHAREPOINT_PWD         = 'GValsa@2024'
        self.SHAREPOINT_URL         = 'https://valsasaudecombr.sharepoint.com/sites'
        self.SHAREPOINT_SITENAME    = 'monitoramento'
        self.SHAREPOINT_DOCS        = 'Shared Documents'

settings = Settings()
