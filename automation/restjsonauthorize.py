import json
import requests
from requests.auth import HTTPBasicAuth
import os
from globalvars import globalvars

class RestJsonRequest:
    def __init__(self,TestCaseId,AndCapInd):
        self.DBname = globalvars.DBNAME
        self.TestCaseId = TestCaseId
        
        self.data_files = os.path.join(os.path.dirname( __file__ ), '..', 'GUIs/data_files')
        JsonTemp = os.path.abspath(os.path.join(self.data_files,"Auth_RestJson_Template.json")) 
        
        self.json_file = open(JsonTemp, "r")        
        self.json_template = json.loads(self.json_file.read())
        self.json_file.close()
        
        if AndCapInd != 0:
            self.json_template["$type"] = "AuthorizeAndCaptureTransaction,http://schemas.evosnap.com/CWS/v2.0/Transactions/Rest"
        
        self.getTestCaseData()
        self.setHighLevelData()
        self.setTenderRequestObject()
        self.setTransactionRequestObject()
        self.setLevel2RequestObject()
        self.setInterchangeRequestObject()
        
        JsonReq = os.path.abspath(os.path.join(self.data_files,"AuthRestJson_Request.json"))        
        self.RestJsonAuthReq = open(JsonReq, "w")
        self.RestJsonAuthReq.write(json.dumps(self.json_template,sort_keys=True, indent=2, separators =(',',':')))
        
        self.RestJsonAuthReq.close()
        self.setParasoftVars()
       
        
    def getTestCaseData(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        r = requests.get(docURL + self.TestCaseId,auth=HTTPBasicAuth('admin','admin'))
        self.TestCase = json.loads(r.text)        
        self.TestCaseInfo = self.TestCase["TestCaseInfo"]
        
    def setHighLevelData(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        r = requests.get(docURL + self.TestCaseId + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.HighLevelData = json.loads(r.text)
        
        self.json_template["ApplicationProfileId"] = self.HighLevelData["Application"]["ApplicationProfileId"]
        self.json_template["MerchantProfileId"] = self.HighLevelData["Merchant"]["MerchantProfileId"]
        
    def setTenderRequestObject(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"        
        r = requests.get(url = docURL + self.TestCase["TenderData"][1:] + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.TenderData = json.loads(r.text)
        
        if self.TestCaseInfo["Workflow"] == "Magensa":
            del self.json_template["Transaction"]["TenderData"]["CardData"]
            del self.json_template["Transaction"]["TenderData"]["CardSecurityData"]
            del self.json_template["Transaction"]["TenderData"]["EcommerceSecurityData"]
            
        #Card Data Populate
        if self.TestCaseInfo["EntryMode"] == "Keyed": #Must get EntryMode from TestCase:TransactionData
            del self.json_template["Transaction"]["TenderData"]["CardData"]["Track2Data"]
            self.json_template["Transaction"]["TenderData"]["CardData"]["Expire"] = self.TenderData["CardData"]["Expire"]
            self.json_template["Transaction"]["TenderData"]["CardData"]["PAN"] = self.TenderData["CardData"]["PAN"]            
        else:
            self.json_template["Transaction"]["TenderData"]["CardData"]["Track2Data"] = self.TenderData["CardData"]["Track2Data"]
            del self.json_template["Transaction"]["TenderData"]["CardData"]["Expire"]
            del self.json_template["Transaction"]["TenderData"]["CardData"]["PAN"]            
        self.json_template["Transaction"]["TenderData"]["CardData"]["CardType"] = self.TenderData["CardData"]["CardType"]    
        
        #Ecomm Security Data Populate
        if "3DSecure" in self.TestCaseInfo.keys():
            self.json_template["Transaction"]["TenderData"]["EcommerceSecurityData"]["TokenData"] = self.TenderData["EcommerceSecurityData"]["TokenData"]
            self.json_template["Transaction"]["TenderData"]["EcommerceSecurityData"]["TokenIndicator"] = self.TenderData["EcommerceSecurityData"]["TokenIndicator"]            
        else:
            del self.json_template["Transaction"]["TenderData"]["EcommerceSecurityData"]
            
        #CVData, AVSData and PINDebit Populate
        ArgVals = set(["CVData","AVSData"])    
        if self.TestCaseInfo["TenderType"] == "Credit" and set([]) == ArgVals & set(self.TestCaseInfo.keys()): #Case with Credit Tender, no CV, AVS            
            del self.json_template["Transaction"]["TenderData"]["CardSecurityData"]           
        elif self.TestCaseInfo["TenderType"] == "Credit" and set(["CVData"]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["CVDataProvided"] = self.TenderData["CardSecurityData"]["CVDataProvided"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["CVData"] = self.TenderData["CardSecurityData"]["CVData"]
            del self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]            
        elif self.TestCaseInfo["TenderType"] == "Credit" and set(["AVSData"]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]["Street"] = self.TenderData["CardSecurityData"]["AVSData"]["Street"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]["PostalCode"] = self.TenderData["CardSecurityData"]["AVSData"]["PostalCode"]            
        elif self.TestCaseInfo["TenderType"] == "Credit" and ArgVals == ArgVals & set(self.TestCaseInfo.keys()):
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]["Street"] = self.TenderData["CardSecurityData"]["AVSData"]["Street"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]["PostalCode"] = self.TenderData["CardSecurityData"]["AVSData"]["PostalCode"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["CVDataProvided"] = self.TenderData["CardSecurityData"]["CVDataProvided"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["CVData"] = self.TenderData["CardSecurityData"]["CVData"]            
        elif self.TestCaseInfo["TenderType"] == "PINDebit" and set([]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["KeySerialNumber"] = self.TenderData["CardSecurityData"]["KeySerialNumber"]
            self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["PIN"] = self.TenderData["CardSecurityData"]["PIN"]
            del self.json_template["Transaction"]["TenderData"]["CardSecurityData"]["AVSData"]
            
    def setTransactionRequestObject(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"        
        r = requests.get(url = docURL + self.TestCase["TransactionData"][1:] + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.TransactionData = json.loads(r.text)
                
        self.json_template["Transaction"]["TransactionData"]["Amount"] = self.TransactionData["Amount"]        
        self.json_template["Transaction"]["TransactionData"]["CurrencyCode"] = self.TransactionData["CurrencyCode"]
        self.json_template["Transaction"]["TransactionData"]["AccountType"] = self.TransactionData["AccountType"]
        self.json_template["Transaction"]["TransactionData"]["CustomerPresent"] = self.TransactionData["CustomerPresent"]
        self.json_template["Transaction"]["TransactionData"]["EntryMode"] = self.TransactionData["EntryMode"]        
            
        if self.TestCaseInfo["IndustryType"] in ["Retail","Restaurant"]:
            self.json_template["Transaction"]["TransactionData"]["EmployeeId"] = self.TransactionData["EmployeeId"]            
        if self.TestCaseInfo["IndustryType"] in ["Restaurant"]:
            self.json_template["Transaction"]["TransactionData"]["TipAmount"] = self.TransactionData["TipAmount"]            
        if self.TestCaseInfo["TenderType"] == "PINDebit":
            self.json_template["Transaction"]["TransactionData"]["CashBackAmount"] = self.TransactionData["CashBackAmount"]            
        else:
            del self.json_template["Transaction"]["TransactionData"]["CashBackAmount"]
            
    def setLevel2RequestObject(self):                    
        if "IsTaxExempt" not in self.TestCaseInfo.keys():    #For Level2            
            del self.json_template["Transaction"]["TransactionData"]["Level2Data"]             
        else:            
            self.json_template["Transaction"]["TransactionData"]["Level2Data"]["BaseAmount"] = self.TransactionData["Level2Data"]["BaseAmount"]
            self.json_template["Transaction"]["TransactionData"]["Level2Data"]["CustomerCode"] = self.TransactionData["Level2Data"]["CustomerCode"]
            self.json_template["Transaction"]["TransactionData"]["Level2Data"]["OrderNumber"] = self.TransactionData["Level2Data"]["OrderNumber"]
            self.json_template["Transaction"]["TransactionData"]["Level2Data"]["TaxExempt"]["IsTaxExempt"] = self.TransactionData["Level2Data"]["TaxExempt"]["IsTaxExempt"]
            self.json_template["Transaction"]["TransactionData"]["Level2Data"]["Tax"]["Amount"] = self.TransactionData["Level2Data"]["Tax"]["Amount"]            
            if self.TestCaseInfo["IsTaxExempt"] == "Exempt":
                self.json_template["Transaction"]["TransactionData"]["Level2Data"]["TaxExempt"]["TaxExemptNumber"] = self.TransactionData["Level2Data"]["TaxExempt"]["TaxExemptNumber"]                
            else:
                del self.json_template["Transaction"]["TransactionData"]["Level2Data"]["TaxExempt"]["TaxExemptNumber"]
                
    def setInterchangeRequestObject(self):        
        if "BillPayment" not in self.TestCaseInfo.keys():
            del self.json_template["Transaction"]["InterchangeData"]
        else:            
            self.json_template["Transaction"]["InterchangeData"]["BillPayment"] = self.HighLevelData["InterchangeData"]["BillPayment"]
            self.json_template["Transaction"]["InterchangeData"]["ExistingDebt"] = self.HighLevelData["InterchangeData"]["ExistingDebt"]
            self.json_template["Transaction"]["InterchangeData"]["CurrentInstallmentNumber"] = self.HighLevelData["InterchangeData"]["CurrentInstallmentNumber"]
            if self.HighLevelData["InterchangeData"]["BillPayment"] == "Installment":
                self.json_template["Transaction"]["InterchangeData"]["TotalNumberOfInstallments"] = self.HighLevelData["InterchangeData"]["TotalNumberOfInstallments"]
            else:
                del self.json_template["Transaction"]["InterchangeData"]["TotalNumberOfInstallments"]
                
    def setParasoftVars(self):
        IdtFile = os.path.abspath(os.path.join(self.data_files,"IdentityToken.csv"))        
        varfile = open(IdtFile, 'w')
        
        varfile.write("MessageType,Environment,IdentityToken,ServiceId\n")
               
        line2 = ""
        if self.TestCaseInfo["MessageType"] == "SOAP":
            line2 = "SOAP,"+ self.TestCaseInfo["Environment"] + "," + self.HighLevelData["Credentials"]["IdentityToken"] +"," + self.HighLevelData["Service"]["ServiceId"]
        elif self.TestCaseInfo["MessageType"] == "REST":
            line2 = "REST," + self.TestCaseInfo["Environment"] + "," + self.HighLevelData["Credentials"]["IdentityToken"] +"," + self.HighLevelData["Service"]["ServiceId"]
        
        varfile.write(line2)                   
        varfile.close()
         
        

    