import os
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json

class QueryBuilder:
    def __init__(self,queryparams):
        self.queryparams = queryparams
        self.dataload = {}
        
        self.createTranslators()
        
    def createTranslators(self):        
        guiarrayvars = ["amounts_var","apprvcds_var","batchids_var","merchprofids_var","ordernums_var","serviceids_var","servicekeys_var","txnids_var"]
        if set(guiarrayvars) & set(self.queryparams) != set([]):
            self.arraytranslator = dict(zip(guiarrayvars,["Amounts","ApprovalCodes","BatchIds","MerchantProfileIds","OrderNumbers","ServiceIds","ServiceKeys","TransactionIds"]))
            self.createArrayStrings()
            
        guienumvars = ["capturestates","cardtypes","txnstates"]    
        if set(guienumvars) & set(self.queryparams) != set([]):
            self.enumtranslator = dict(zip(guienumvars,["CaptureStates","CardTypes","TransactionStates"]))
            self.createEnumStrings()
         
        guifixedvars = ["querytype_var","includereltd_var","txndetlfrmt_var"]
        if set(guifixedvars) & set(self.queryparams) != set([]):
            self.fixedtranslator = dict(zip(guifixedvars,["QueryType","IncludeRelated","TransactionDetailFormat"]))
            self.createFixedStrings()
        
        guitimevars = ["txntimestart_menuitemvar","txntimeend_menuitemvar","capturetimestart_menuitemvar","capturetimeend_menuitemvar"]
        if set(guitimevars) & set(self.queryparams) != set([]):
            self.timetranslator = dict(zip(guitimevars,["TransactionDateTime:StartDateTime","TransactionDateTime:EndDateTime","CaptureDateTime:StartDateTime","CaptureDateTime:EndDateTime"]))
            self.createDateTimeStrings() 
        
    def createArrayStrings(self):
        for guivar, CWSvar in self.arraytranslator.items():
            if guivar in self.queryparams.keys():                
                for value in self.queryparams[guivar]:
                    if CWSvar in self.dataload:
                        self.dataload[CWSvar] = self.dataload[CWSvar] + '<ns1:string xmlns:ns1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">' + value + '</ns1:string>\n'
                    else:
                        self.dataload[CWSvar] = '<ns1:string xmlns:ns1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">' + value + '</ns1:string>\n'
    
    def createEnumStrings(self):
        for guivar, CWSvar in self.enumtranslator.items():
            if guivar in self.queryparams.keys():
                for value in self.queryparams[guivar]:
                    if CWSvar in self.dataload:
                        self.dataload[CWSvar] = self.dataload[CWSvar] + '<ns2:' + CWSvar + ' xmlns:ns2="http://schemas.evosnap.com/CWS/v2.0/Transactions">' + value + '</ns2:' + CWSvar + '>\n'
                    else:
                        self.dataload[CWSvar] = '<ns2:' + CWSvar + ' xmlns:ns2="http://schemas.evosnap.com/CWS/v2.0/Transactions">' + value + '</ns2:' + CWSvar + '>\n'
                    
    def createFixedStrings(self):
        for guivar, CWSvar in self.fixedtranslator.items():
            if guivar in self.queryparams.keys():
                for value in self.queryparams[guivar]:
                    self.dataload[CWSvar] = value
            
    def createDateTimeStrings(self):
        currtimevars = set(["txntimestart_menuitemvar","capturetimestart_menuitemvar"]) & set(list(self.queryparams.keys()))        
        for var in list(currtimevars):
            if var.find("txn") != -1:
                times = self.getDateTime(self.queryparams["txntimestart_menuitemvar"][0],self.queryparams["txntimeend_menuitemvar"][0])                
                self.dataload[self.timetranslator["txntimestart_menuitemvar"]] = times[0].split(".")[0] + "Z"
                self.dataload[self.timetranslator["txntimeend_menuitemvar"]] = times[1].split(".")[0] + "Z"
            elif var.find("capture") != -1:
                times = self.getDateTime(self.queryparams["capturetimestart_menuitemvar"][0],self.queryparams["capturetimeend_menuitemvar"][0])
                self.dataload[self.timetranslator["capturetimestart_menuitemvar"]] = times[0].split(".")[0] + "Z"
                self.dataload[self.timetranslator["capturetimeend_menuitemvar"]] = times[1].split(".")[0] + "Z"
                                    
    def getDateTime(self,starttime,endtime):
        times = []
        today = datetime.datetime.utcnow()
        for timestr in [starttime,endtime]:
            if timestr == "Now":
                times.append(today.isoformat())                
            elif timestr == "One Hour Ago":
                dt = today - datetime.timedelta(hours=1)
                times.append(dt.isoformat())                
            elif timestr == "Four Hours Ago":
                dt = today - datetime.timedelta(hours=4)
                times.append(dt.isoformat())                
            elif timestr == "Eight Hours Ago":
                dt = today - datetime.timedelta(hours=8)
                times.append(dt.isoformat())                
            elif timestr == "One Day Ago":
                dt = today - datetime.timedelta(days=1)
                times.append(dt.isoformat())                
            elif timestr == "Two Days Ago":
                dt = today - datetime.timedelta(days=2)
                times.append(dt.isoformat())                
            elif timestr == "One Week Ago":
                dt = today - datetime.timedelta(days=7)
                times.append(dt.isoformat())                
            elif timestr == "One Month Ago":
                dt = today - datetime.timedelta(days=30)
                times.append(dt.isoformat())                
        return times

#####-----Functions ----- #####
    
def getCredentials(DBname):
    url = "http://localhost:2480/cluster/" + DBname + "/Credentials/50"
    r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
    creds = {}
    for record in json.loads(r1.text)["result"]:
        creds[record["ServiceKey"]+"-"+record["Environment"]+"-"+record["MessageType"]] = record["@rid"]
    return creds

def buildDataSource(data,recordid):
    data_files = os.path.join(os.path.dirname( __file__ ), '..', 'GUIs/data_files')       
    if recordid == None:
        credsourcefile = os.path.abspath(os.path.join(data_files,"IdentityToken.csv"))
        
    