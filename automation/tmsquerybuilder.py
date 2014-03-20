import os
import datetime

class QueryBuilder:
    def __init__(self,queryparams):
        self.queryparams = queryparams
        self.dataload = {}
        
        self.createTranslators()
        self.createArrayStrings()        
        
    def createTranslators(self):        
        guiarrayvars = ["amounts_var","apprvcds_var","batchids_var","merchprofids_var","ordernums_var","serviceids_var","servicekeys_var","txnids_var"]
        CWSarrayvars = ["Amounts","ApprovalCodes","BatchIds","MerchantProfileIds","OrderNumbers","ServiceIds","ServiceKeys","TransactionIds"]
        guienumvars = ["capturestates","cardtypes","txnstates"] 
        CWSenumvars = ["CaptureStates","CardTypes","TransactionStates"]
        guifixedvars = ["querytype_var","includereltd_var","txndetlfrmt_var"]
        CWSfixedvars = ["QueryType","IncludeRelated","TransactionDetailFormat"]
        guitimevars = ["txntimestart_menuitemvar","txntimeend_menuitemvar","capturetimestart_menuitemvar","capturetimeend_menuitemvar"]
        CWStimevars = ["TransactionDateTime:StartDateTime","TransactionDateTime:EndDateTime","CaptureDateTime:StartDateTime","CaptureDateTime:EndDateTime"]
        self.arraytranslator = dict(zip(guiarrayvars,CWSarrayvars))
        self.enumtranslator = dict(zip(guienumvars,CWSenumvars))
        self.fixedtranslator = dict(zip(guifixedvars,CWSfixedvars))
        self.timetranslator = dict(zip(guitimevars,CWStimevars))
        
    def createArrayStrings(self):
        for guivar, CWSvar in self.arraytranslator.items():
            if guivar in self.queryparams.keys():                
                for value in self.queryparams[guivar]:
                    self.dataload[CWSvar] = self.dataload[CWSvar] + '<ns1:string xmlns:ns1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">' + value + '</ns1:string>\n'
                                    
    def getDateTime(self,starttime,endtime):
        times = {}
        today = datetime.datetime.utcnow()
        for timestr in [starttime,endtime]:
            if timestr == "Now":
                times[timestr] = today.isoformat()                
            elif timestr == "One Hour Ago":
                times[timestr] = today - datetime.timedelta(hours=1)
                times[timestr].isoformat()
            elif timestr == "Four Hours Ago":
                times[timestr] = today - datetime.timedelta(hours=4)
                times[timestr].isoformat()
            elif timestr == "Eight Hours Ago":
                times[timestr] = today - datetime.timedelta(hours=8)
                times[timestr].isoformat()
            elif timestr == "One Day Ago":
                times[timestr] = today - datetime.timedelta(days=1)
                times[timestr].isoformat()
            elif timestr == "Two Days Ago":
                times[timestr] = today - datetime.timedelta(days=2)
                times[timestr].isoformat()
            elif timestr == "One Week Ago":
                times[timestr] = today - datetime.timedelta(days=7)
                times[timestr].isoformat()
            elif timestr == "One Month Ago":
                times[timestr] = today - datetime.timedelta(days=30)
                times[timestr].isoformat()
    