import xml.etree.ElementTree as ET
import json
import requests
from requests.auth import HTTPBasicAuth
import re
import os
from globalvars import globalvars

class SOAPRequest:
    def __init__(self,TestCaseId,AndCapInd):
        self.DBname = globalvars.DBNAME
        self.TestCaseId = TestCaseId
        self.AndCapInd = AndCapInd
        
        self.data_files = os.path.join(os.path.dirname( __file__ ), '..', 'GUIs/data_files')
        SOAPTemp = os.path.abspath(os.path.join(self.data_files,"Auth_SOAP_Template.xml"))        
        self.AuthTemplate = ET.parse(SOAPTemp)    
        self.root = self.AuthTemplate.getroot()    
        #TenderData = self.root[0][0][1][4]
        #CardData = self.root[0][0][1][4][5]
        #CardSecurityData = self.root[0][0][1][4][6]
        #AVSData = self.root[0][0][1][4][6][0]
        #EcommerceSecurityData = self.root[0][0][1][4][7]
        #TransactionData = self.root[0][0][1][5]
        #Level2Data = self.root[0][0][1][5][22]
        #InterchangeData = self.root[0][0][1][6]
        
        self.getTestCaseData()
        self.setHighLevelData()
        self.setTenderRequestObject()
        self.setTransactionRequestObject()
        self.setLevel2RequestObject()
        self.setInterchangeRequestObject()        
        ET.register_namespace("SOAP-ENV","http://schemas.xmlsoap.org/soap/envelope/")
        
        SOAPReq = os.path.abspath(os.path.join(self.data_files,"AuthSOAP_Request.xml"))        
        self.AuthTemplate.write(SOAPReq)
        self.handleNamespaces()
        self.setParasoftVars()
    
    
    def getTestCaseData(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        r = requests.get(docURL + self.TestCaseId,auth=HTTPBasicAuth('admin','admin'))
        self.TestCase = json.loads(r.text)        
        self.TestCaseInfo = self.TestCase["TestCaseInfo"]
    
    def getParentNode(self,parenttagname):
        namespaces = ["http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing","http://schemas.evosnap.com/CWS/v2.0/Transactions","http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard","http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard/Pro"]
        parentnode = ""        
        for ns in namespaces:
            if self.root.find(".//{" + ns + "}" + parenttagname) != None:                
                parentnode = self.root.find(".//{" + ns + "}" + parenttagname)
        return parentnode
    
    def getChildNode(self,parentnode,childtagname):         
        namespaces = ["http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing","http://schemas.evosnap.com/CWS/v2.0/Transactions","http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard","http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard/Pro"]
        parenttag = parentnode.tag
        childnode = ""        
        for ns in namespaces:
            if self.root.find(".//" + parenttag + "/{" + ns + "}" + childtagname) != None:                
                childnode = self.root.find(".//" + parenttag + "/{" + ns + "}" + childtagname)
        return childnode    
        
    def setHighLevelData(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        r = requests.get(docURL + self.TestCaseId + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.HighLevelData = json.loads(r.text)        
        AuthNode = self.getParentNode("Authorize")
        self.getChildNode(AuthNode,"workflowId").text = self.HighLevelData["Service"]["ServiceId"]
        self.getChildNode(AuthNode,"applicationProfileId").text = self.HighLevelData["Application"]["ApplicationProfileId"]
        self.getChildNode(AuthNode,"merchantProfileId").text = self.HighLevelData["Merchant"]["MerchantProfileId"]
    
        
    def setTenderRequestObject(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"        
        r = requests.get(url = docURL + self.TestCase["TenderData"][1:] + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.TenderData = json.loads(r.text)        
        TenderDataNode = self.getParentNode("TenderData")
        if self.TestCaseInfo["Workflow"] == "Magensa":
            TenderDataNode.remove(self.getChildNode(TenderDataNode,"CardData"))
            TenderDataNode.remove(self.getChildNode(TenderDataNode,"CardSecurityData"))
            TenderDataNode.remove(self.getChildNode(TenderDataNode,"EcommerceSecurityData"))            
            return        
        
        CardDataNode = self.getParentNode("CardData")
        EcommSecNode = self.getParentNode("EcommerceSecurityData")
        CardSecNode = self.getParentNode("CardSecurityData")
        AVSNode = self.getParentNode("AVSData")
        #Card Data Populate
        if self.TestCaseInfo["EntryMode"] == "Keyed": #Must get EntryMode from TestCase:TransactionData
            CardDataNode.remove(self.getChildNode(CardDataNode,"Track2Data"))
            self.getChildNode(CardDataNode,"Expire").text = self.TenderData["CardData"]["Expire"]
            self.getChildNode(CardDataNode,"PAN").text = self.TenderData["CardData"]["PAN"]            
        else:
            self.getChildNode(CardDataNode,"Track2Data").text = self.TenderData["CardData"]["Track2Data"]
            CardDataNode.remove(self.getChildNode(CardDataNode,"PAN"))
            CardDataNode.remove(self.getChildNode(CardDataNode,"Expire"))            
        self.getChildNode(CardDataNode,"CardType").text = self.TenderData["CardData"]["CardType"]    
        
        #Ecomm Security Data Populate
        if "3DSecure" in self.TestCaseInfo.keys():
            self.getChildNode(EcommSecNode,"TokenData").text = self.TenderData["EcommerceSecurityData"]["TokenData"]
            self.getChildNode(EcommSecNode,"TokenIndicator").text = self.TenderData["EcommerceSecurityData"]["TokenIndicator"]            
        else:
            TenderDataNode.remove(self.getChildNode(TenderDataNode,"EcommerceSecurityData"))            
        
        #CVData, AVSData and PINDebit Populate
        ArgVals = set(["CVData","AVSData"])    
        if self.TestCaseInfo["TenderType"] == "Credit" and set([]) == ArgVals & set(self.TestCaseInfo.keys()): #Case with Credit Tender, no CV, AVS            
            TenderDataNode.remove(self.getChildNode(TenderDataNode,"CardSecurityData"))            
        elif self.TestCaseInfo["TenderType"] == "Credit" and set(["CVData"]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.getChildNode(CardSecNode,"CVDataProvided").text = self.TenderData["CardSecurityData"]["CVDataProvided"]
            self.getChildNode(CardSecNode,"CVData").text = self.TenderData["CardSecurityData"]["CVData"]
            CardSecNode.remove(self.getChildNode(CardSecNode,"AVSData"))            
        elif self.TestCaseInfo["TenderType"] == "Credit" and set(["AVSData"]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.getChildNode(AVSNode,"Street").text = self.TenderData["CardSecurityData"]["AVSData"]["Street"]
            self.getChildNode(AVSNode,"PostalCode").text = self.TenderData["CardSecurityData"]["AVSData"]["PostalCode"]            
        elif self.TestCaseInfo["TenderType"] == "Credit" and ArgVals == ArgVals & set(self.TestCaseInfo.keys()):
            self.getChildNode(AVSNode,"Street").text = self.TenderData["CardSecurityData"]["AVSData"]["Street"]
            self.getChildNode(AVSNode,"PostalCode").text = self.TenderData["CardSecurityData"]["AVSData"]["PostalCode"]
            self.getChildNode(CardSecNode,"CVDataProvided").text = self.TenderData["CardSecurityData"]["CVDataProvided"]
            self.getChildNode(CardSecNode,"CVData").text = self.TenderData["CardSecurityData"]["CVData"]            
        elif self.TestCaseInfo["TenderType"] == "PINDebit" and set([]) == ArgVals & set(self.TestCaseInfo.keys()):
            self.getChildNode(CardSecNode,"KeySerialNumber").text = self.TenderData["CardSecurityData"]["KeySerialNumber"]
            self.getChildNode(CardSecNode,"PIN").text = self.TenderData["CardSecurityData"]["PIN"]
            CardSecNode.remove(self.getChildNode(CardSecNode,"AVSData"))            
    
    def setTransactionRequestObject(self):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"        
        r = requests.get(url = docURL + self.TestCase["TransactionData"][1:] + "/*:1",auth=HTTPBasicAuth('admin','admin'))
        self.TransactionData = json.loads(r.text)
        TxnNode = self.getParentNode("TransactionData")        
        self.getChildNode(TxnNode,"Amount").text = self.TransactionData["Amount"]        
        self.getChildNode(TxnNode,"CurrencyCode").text = self.TransactionData["CurrencyCode"]
        self.getChildNode(TxnNode,"AccountType").text = self.TransactionData["AccountType"]
        self.getChildNode(TxnNode,"CustomerPresent").text = self.TransactionData["CustomerPresent"]
        self.getChildNode(TxnNode,"EntryMode").text = self.TransactionData["EntryMode"]        
            
        if self.TestCaseInfo["IndustryType"] in ["Retail","Restaurant","MOTO"]:
            self.getChildNode(TxnNode,"EmployeeId").text = self.TransactionData["EmployeeId"]            
        if self.TestCaseInfo["IndustryType"] in ["Restaurant"]:
            self.getChildNode(TxnNode,"TipAmount").text = self.TransactionData["TipAmount"]            
        if self.TestCaseInfo["TenderType"] == "PINDebit":
            self.getChildNode(TxnNode,"CashBackAmount").text = self.TransactionData["CashBackAmount"]            
        else:
            TxnNode.remove(self.getChildNode(TxnNode,"CashBackAmount"))
        
    def setLevel2RequestObject(self):
        TxnNode = self.getParentNode("TransactionData")            
        if "IsTaxExempt" not in self.TestCaseInfo.keys():    #For Level2            
            TxnNode.remove(self.getChildNode(TxnNode,"Level2Data"))             
        else:
            Level2Node = self.getParentNode("Level2Data")
            TaxExemptNode = self.getParentNode("TaxExempt")
            TaxNode = self.getParentNode("Tax")
            self.getChildNode(Level2Node,"BaseAmount").text = self.TransactionData["Level2Data"]["BaseAmount"]
            self.getChildNode(Level2Node,"CustomerCode").text = self.TransactionData["Level2Data"]["CustomerCode"]
            self.getChildNode(Level2Node,"OrderNumber").text = self.TransactionData["Level2Data"]["OrderNumber"]
            self.getChildNode(TaxExemptNode,"IsTaxExempt").text = self.TransactionData["Level2Data"]["TaxExempt"]["IsTaxExempt"]
            self.getChildNode(TaxNode,"IsTaxExempt").text = self.TransactionData["Level2Data"]["Tax"]["Amount"]            
            if self.TestCaseInfo["IsTaxExempt"] == "Exempt":
                self.getChildNode(TaxExemptNode,"TaxExemptNumber").text = self.TransactionData["Level2Data"]["TaxExempt"]["TaxExemptNumber"]                
            else:
                TaxExemptNode.remove(self.getChildNode(TaxExemptNode,"TaxExemptNumber"))
                
    def setInterchangeRequestObject(self):
        transNode = self.getParentNode("transaction")
        if "BillPayment" not in self.TestCaseInfo.keys():
            transNode.remove(self.getChildNode(transNode,"InterchangeData"))
        else:
            InterchangeNode = self.getParent("InterchangeData")
            self.getChildNode(InterchangeNode,"BillPayment").text = self.HighLevelData["InterchangeData"]["BillPayment"]
            self.getChildNode(InterchangeNode,"ExistingDebt").text = self.HighLevelData["InterchangeData"]["ExistingDebt"]
            self.getChildNode(InterchangeNode,"CurrentInstallmentNumber").text = self.HighLevelData["InterchangeData"]["CurrentInstallmentNumber"]
            if self.HighLevelData["InterchangeData"]["BillPayment"] == "Installment":
                self.getChildNode(InterchangeNode,"TotalNumberOfInstallments").text = self.HighLevelData["InterchangeData"]["TotalNumberOfInstallments"]
            else:
                InterchangeNode.remove(self.getChildNode(InterchangeNode,"TotalNumberOfInstallments"))
            
    def handleNamespaces(self):
        AuthReq = os.path.abspath(os.path.join(self.data_files,"AuthSOAP_Request.xml"))        
        newfile = open(AuthReq, 'r+')        
        NewLineList = newfile.readlines()
        newfile.seek(0,0)        
        NewLineList[0] = '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard/Pro" xmlns:ns3="http://schemas.evosnap.com/CWS/v2.0/Transactions" xmlns:ns4="http://schemas.evosnap.com/CWS/v2.0/Transactions/Bankcard" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        if self.AndCapInd == 0:
            NewLineList[2] = '<Authorize xmlns="http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing">\n'            
        else:
            NewLineList[2] = '<AuthorizeAndCapture xmlns="http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing">\n'
            NewLineList[len(NewLineList)- 3] = '</AuthorizeAndCapture>\n'
        NewLineList[3] = '<sessionToken>${Test 1: SignOnWithTokenResult}</sessionToken>\n'
        NewLineList[4] = '<transaction xsi:type="ns2:BankcardTransactionPro">\n'
        for line in NewLineList:
            if line.find('<ns4:TransactionData') == -1:
                line = re.sub(r'ns1:',"",line)
            else:
                line = re.sub(r'ns1:',"ns2:",line)
            line = re.sub(r'ns5:',"ns2:",line)
            newfile.write(line)
        newfile.truncate()    
        newfile.close()
        
    def setParasoftVars(self):
        IdtFile = os.path.abspath(os.path.join(self.data_files,"IdentityToken.csv"))        
        varfile = open(IdtFile, 'w')
        
        soapaction = ""
        if self.AndCapInd == 0:
            soapaction = 'http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing/ICwsTransactionProcessing/Authorize'
        else:
            soapaction = 'http://schemas.evosnap.com/CWS/v2.0/TransactionProcessing/ICwsTransactionProcessing/AuthorizeAndCapture'            
        
        varfile.write("MessageType,Environment,SOAPAction,IdentityToken\n")
               
        line2 = ""
        if self.TestCaseInfo["MessageType"] == "SOAP":
            line2 = "SOAP,"+ self.TestCaseInfo["Environment"] + "," + soapaction + "," + self.HighLevelData["Credentials"]["IdentityToken"]
        elif self.TestCaseInfo["MessageType"] == "REST":
            line2 = "REST," + self.TestCaseInfo["Environment"] + "," + soapaction + "," + self.HighLevelData["Credentials"]["IdentityToken"]
        
        varfile.write(line2)                   
        varfile.close()
        

                