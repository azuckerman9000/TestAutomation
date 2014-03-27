################Global Variables###################
global DBNAME
DBNAME = "CWSData"

global PROPERTYTYPES
PROPERTYTYPES = ["STRING","INTEGER","LINK","LINKLIST","EMBEDDEDLIST","EMBEDDEDMAP"]

global TENDERTYPES
TENDERTYPES = ["Credit","PINDebit"]

global MESSAGETYPES
MESSAGETYPES = ["SOAP","REST"]

global HOSTNAMES
HOSTNAMES = ["EVO HostCap TestHost","EVO TermCap TestHost","EVO HostCap Sandbox","EVO TermCap Sandbox","EVO TermCap AutoResponder","EVO TermCap TPS","EVO HostCap TPS"]

global INDUSTRYTYPES
INDUSTRYTYPES = ["Retail","Restaurant","MOTO","Ecommerce"]

global WORKFLOWS
WORKFLOWS = ["None","Magensa","ReD"]

global ENVIRONMENTS
ENVIRONMENTS = ["TEST","CERT","PROD"]

global CARDTYPES
CARDTYPES = ["Visa","MasterCard","Discover","AmericanExpress"]

global OPTIONALARGS
OPTIONALARGS = ["CVData","AVSData","BillPay"]

global LEVEL2ARGS
LEVEL2ARGS = ["Exempt","NotExempt"]

global BILLPAYARGS
BILLPAYARGS = ["Recurring","Installment"]