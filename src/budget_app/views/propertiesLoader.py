from properties import *

def loadProperties(c,page):
    
    #Global Properties

    
    #Page Properties
    if page == 'reuse':
        c['urlOpenData'] = urlOpenData
        c['urlCatalogoPresupuesto'] = urlCatalogoPresupuesto
        c['urlCodeRepo'] = urlCodeRepo
        c['urlLicenseRepo'] = urlLicenseRepo
        c['urlInstallRepo'] = urlInstallRepo
        c['urlCivioFundation'] = urlCivioFundation
    elif page == 'welcome':
        c['urlOpenData'] = urlOpenData