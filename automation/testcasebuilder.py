import json
import requests
import re
from requests.auth import HTTPBasicAuth
import sys
import tkinter as tk
from globalvars import globalvars

class Transaction:
    def __init__(self,TenderType,MessageType,Host,IndustryType,Workflow,Environment,CardType, *args): #*args values can be [CVData, AVSData, 3DSecure, Level2, BillPay, Recurring or Installment, Exempt or NotExempt]
        
        
        self.args = args
        if "BillPay" in self.args:            
            if "Recurring" in self.args:
                self.BillPayment = "Recurring"
            elif "Installment" in self.args:
                self.BillPayment = "Installment"
        else:
            self.BillPayment = ""
        
        if "Level2"    in self.args:
            if "Exempt" in self.args:
                self.IsTaxExempt = "Exempt"
            elif "NotExempt" in self.args:
                self.IsTaxExempt = "NotExemptTaxInfoProvided"
        else:
            self.IsTaxExempt = ""
        
        self.TenderType = TenderType    
        self.MessageType = MessageType
        self.Host = Host        
        self.IndustryType = IndustryType
        self.Workflow = Workflow
        self.Environment = Environment
        self.CardType = CardType
        self.DBname = globalvars.DBNAME
        
        self.dataRules() #Checks to see that inputs can build a valid test case
        self.getTestCaseRecord() #Checks if test case already exists in DB based on input params. sets self.TestCaseRecordId to record id, if found.
        
        # Data values
        self.ServiceId = ""
        self.MerchantProfileId = ""    
        self.EntryMode = ""
        self.CustomerPresent = ""        
        self.ServiceKey = ""        
        self.ApplicationProfileId = ""
        self.PAN = ""    
        
        # Record Ids
        self.ServiceRecordId = ""
        self.CredentialsRecordId = ""        
        self.MerchantRecordId = ""
        self.ApplicationRecordId = ""
        self.CardRecordId = ""
        self.CardSecurityRecordId = ""
        self.EcommerceSecurityRecordId = ""    
        self.TenderRecordId = ""
        self.TransactionRecordId = ""
        self.Level2RecordId = ""
        self.InterchangeRecordId = ""
        
        if self.TestCaseRecordId == "":
            self.createNewTestCase() #Builds new test case record if getTestCaseRecord() does not find existing test case in DB
        #if self.TestCaseRecordId == "":
            #self.getService()
        
    def getService(self):
        URL = "http://localhost:2480/cluster/" + self.DBname + "/Service/50"    
        r1 = requests.get(URL, auth=HTTPBasicAuth('admin','admin'))
        svc_resp = json.loads(r1.text)
        
        for record in svc_resp["result"]:
            if self.Host == record["Host"] and self.Workflow == record["Workflow"]:
                self.ServiceId = record["ServiceId"]
                self.ServiceRecordId = record["@rid"]
                break
            else:
                continue
        
        if self.ServiceId == "":
            print("No Service record with Host=" + self.Host + ", and/or Workflow=" + self.Workflow + ", in DB.")
            sys.exit()
        
    def getMerchant(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/Merchant/100"        
        r1 = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        merch_resp = json.loads(r1.text)
        
        possiblemerchants = {}
        for record in merch_resp["result"]:
            if self.IndustryType == record["IndustryType"] and self.ServiceRecordId == record["ServiceId"] and self.MessageType == record["MessageType"]:
                possiblemerchants[record["MerchantProfileId"]] = record["@rid"]
        if len(possiblemerchants.keys()) > 1:                        
            while self.MerchantProfileId == "":
                popup = MerchantSelectFrame(**possiblemerchants)
                popup.master.title("Select Merchant")
                popup.mainloop()
                self.MerchantProfileId = popup.rectext["MerchantProfileId"]
                self.EntryMode = popup.rectext["EntryMode"]
                self.CustomerPresent = popup.rectext["CustomerPresent"]
                self.MerchantRecordId = popup.rectext["@rid"]
        elif len(possiblemerchants.keys()) == 1:
            docURL = "http://localhost:2480/document/" + self.DBname + "/"        
            r = requests.get(docURL + list(possiblemerchants.values())[0][1:], auth=HTTPBasicAuth('admin','admin'))        
            record = json.loads(r.text)
            self.MerchantProfileId = record["MerchantProfileId"]
            self.EntryMode = record["EntryMode"]
            self.CustomerPresent = record["CustomerPresent"]
            self.MerchantRecordId = record["@rid"]              
    
        if self.MerchantProfileId == "":
            print("No Merchant record with IndustryType=" + self.IndustryType + ", and/or tied to ServiceId=" + self.ServiceId + ", in DB.")
            sys.exit()        
    
    def getCredentials(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/Credentials"    
        r1 = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        cred_resp = json.loads(r1.text)
        
        for record in cred_resp["result"]:
            if self.MessageType == record["MessageType"] and self.Environment == record["Environment"] and self.ServiceRecordId in record["ServiceId"]:                
                self.ServiceKey = record["ServiceKey"]
                self.CredentialsRecordId = record["@rid"]
                break                        
            else:
                continue                            
        
        if self.ServiceKey == "":
            print("No Credential record with MessageType=" + self.MessageType + ", and/or Environment=" + self.Environment + " and/or tied to ServiceId=" + self.ServiceId + ", in DB.")
            sys.exit()
            
    def getApplication(self):
        clustURL = "http://localhost:2480/cluster/"    + self.DBname + "/Application"
        r1 = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        app_resp = json.loads(r1.text)
        
        for record in app_resp["result"]:
            if self.CredentialsRecordId == record["ServiceKey"]:
                self.ApplicationProfileId = record["ApplicationProfileId"]
                self.ApplicationRecordId = record["@rid"]
                break
            else:
                continue
    
        if self.ApplicationProfileId == "":
            print("No Application record tied to ServiceKey=" + self.ServiceKey)
            sys.exit()
            
    def getCardData(self):
        clustURL = "http://localhost:2480/cluster/"    + self.DBname + "/CardData"
        r1 = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        card_resp = json.loads(r1.text)
        for record in card_resp["result"]:
            if self.CardType == record["CardType"] and self.Environment == record["Environment"]:
                self.CardRecordId = record["@rid"]
                self.PAN = record["PAN"]
                break    
            else:
                continue
                
        if self.PAN == "":
            print("No CardData record with CardType=" + self.CardType + " and/or Environment=" + self.Environment)
            sys.exit()
    
    def getTenderClasses(self): #Updated method with self.args instead of TenderType
        clustURL = "http://localhost:2480/cluster/"    + self.DBname + "/"        
        if "AVSData" in self.args and "CVData" in self.args and "IntlAVSData" not in self.args:
            r1 = requests.get(url = clustURL + "CardSecurityData/50", auth=HTTPBasicAuth('admin','admin'))
            cardsec_resp = json.loads(r1.text)
            for record in cardsec_resp["result"]:
                if "AVSData" in record.keys() and record["PAN"] == self.PAN and record["CVDataProvided"] == "Provided":
                    self.CardSecurityRecordId = record["@rid"]
                    break
        elif "AVSData" in self.args and "CVData" not in self.args and "IntlAVSData" not in self.args:
            r1 = requests.get(url = clustURL + "CardSecurityData", auth=HTTPBasicAuth('admin','admin'))
            cardsec_resp = json.loads(r1.text)
            for record in cardsec_resp["result"]:
                if "AVSData" in record.keys() and record["PAN"] == self.PAN and record["CVDataProvided"] == "NotSet":
                    self.CardSecurityRecordId = record["@rid"]
                    break
        elif "AVSData" not in self.args and "CVData" in self.args and "IntlAVSData" not in self.args:
            r1 = requests.get(url = clustURL + "CardSecurityData", auth=HTTPBasicAuth('admin','admin'))
            cardsec_resp = json.loads(r1.text)
            for record in cardsec_resp["result"]:
                if record["CVDataProvided"] == "Provided" and self.PAN == record["PAN"] and "AVSData" not in record.keys():
                    self.CardSecurityRecordId = record["@rid"]
                    break
        elif "IntlAVSData" in self.args:
            r1 = requests.get(url = clustURL + "CardSecurityData", auth=HTTPBasicAuth('admin','admin'))
            cardsec_resp = json.loads(r1.text)
            for record in cardsec_resp["result"]:
                if "IntlAVSData" in record.keys() and self.PAN == record["PAN"]:
                    self.CardSecurityRecordId = record["@rid"]
                    break
        if "3DSecure" in self.args:            
            r1 = requests.get(url = clustURL + "EcommerceSecurityData", auth=HTTPBasicAuth('admin','admin'))
            ecomm_resp = json.loads(r1.text)
            for record in ecomm_resp["result"]:
                if self.PAN == record["PAN"]:
                    self.EcommerceSecurityRecordId = record["@rid"]
                    break
        if self.TenderType == "PINDebit":
            r1 = requests.get(url = clustURL + "CardSecurityData", auth=HTTPBasicAuth('admin','admin'))
            cardsec_resp = json.loads(r1.text)
            for record in cardsec_resp["result"]:
                if record["PAN"] == self.PAN and "PIN" in record.keys():
                    self.CardSecurityRecordId = record["@rid"]
                    break            
        if self.Workflow == "Magensa":            
            self.CardRecordId = ""
            print("Must manually swipe Card for Data.")        
    
    def checkForTenderRecord(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/"
        PresentRecords = {}
        MissingRecords = []
        if self.CardRecordId != "":
            PresentRecords["CardData"] = self.CardRecordId
        else:
            MissingRecords.append("CardData")
        if self.CardSecurityRecordId != "":
            PresentRecords["CardSecurityData"] = self.CardSecurityRecordId
        else:
            MissingRecords.append("CardSecurityData")    
        if self.EcommerceSecurityRecordId != "":
            PresentRecords["EcommerceSecurityData"] = self.EcommerceSecurityRecordId
        else:
            MissingRecords.append("EcommerceSecurityData")    
        r1 = requests.get(url = clustURL + "TenderData", auth=HTTPBasicAuth('admin','admin'))        
        tender_resp = json.loads(r1.text)
        for record in tender_resp["result"]:
            if set(PresentRecords.keys()) == set(PresentRecords.keys()) & set(record.keys()) and set(MissingRecords) - set(record.keys()) == set(MissingRecords) & set(record.keys()):
                if set(PresentRecords.values()) == set(PresentRecords.values()) & set(record.values()):
                    self.TenderRecordId = record["@rid"]
                    break
        if self.TenderRecordId == "":
            self.createTenderRecord(PresentRecords)
        
    def createTenderRecord(self, PresentRecords):            
        docURL = "http://localhost:2480/document/" + self.DBname
        headers = {"content-type":"application/json"}
        payload = dict([("@class","TenderData"),("TenderType",self.TenderType)] + list(PresentRecords.items()))        
        r = requests.post(docURL, headers=headers, data=json.dumps(payload), auth=HTTPBasicAuth('admin','admin'))
        self.TenderRecordId = r.text            


    def getInterchangeData(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/InterchangeData"
        if self.BillPayment != "":
            r1 = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
            inter_resp = json.loads(r1.text)
            for record in inter_resp["result"]:
                if self.BillPayment == record["BillPayment"]:
                    self.InterchangeRecordId = record["@rid"]
                    break
    
    def getTransactionData(self): #updated method to account for self.args instad of self.TenderType
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/"
        r1 = requests.get(clustURL + "TransactionData/100", auth=HTTPBasicAuth('admin','admin'))
        txn_resp = json.loads(r1.text)
        for record in txn_resp["result"]:
            if self.EntryMode == record["EntryMode"] and self.TenderType == record["TenderType"] and self.IndustryType == record["IndustryType"]:
                if "Level2" in self.args and self.CustomerPresent == record["CustomerPresent"]:
                    self.getLvl2Data()
                    if "Level2Data" in record.keys() and self.Level2RecordId == record["Level2Data"]:
                        self.TransactionRecordId = record["@rid"]
                        break
                    elif  "Level2Data" not in record.keys():
                        self.createLvl2TransactionRecord(record)
                        break
                elif "BillPay" in self.args and record["CustomerPresent"] == "BillPayment":
                    self.TransactionRecordId = record["@rid"]
                    break
                elif set([]) == set(["Level2","Billpay"]) & set(self.args) and self.CustomerPresent == record["CustomerPresent"]:            
                    self.TransactionRecordId = record["@rid"]
                    break    
    
    def getLvl2Data(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/"
        r = requests.get(clustURL + "Level2Data", auth=HTTPBasicAuth('admin','admin'))
        lvl2_resp = json.loads(r.text)
        for record in lvl2_resp["result"]:
            if self.PAN == record["PAN"] and self.IsTaxExempt == record["TaxExempt"["IsTaxExempt"]]:
                self.Level2RecordId = record["@rid"]
                break
                
    def createLvl2TransactionRecord(self,TxnRecord):
        docURL = "http://localhost:2480/document/" + self.DBname
        headers = {"content-type":"application/json"}
        TxnRecord["Level2Data"] = self.Level2RecordId
        del TxnRecord["@rid"]
        del TxnRecord["@version"]
        r = requests.post(docURL, headers=headers, data=json.dumps(TxnRecord), auth=HTTPBasicAuth('admin','admin'))
        self.TransactionRecordId = r.text
    
    def getTestCaseRecord(self):
        TestCaseParams = {}
        for key, value in self.__dict__.items():
            if value != "" and key != "args":
                TestCaseParams[key] = value
        for item in list(set(globalvars.OPTIONALARGS) & set(self.args)):
            TestCaseParams[item] = True
            
        self.TestCaseRecordId = ""        
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/TestCase/100"    
        r = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        testcase_resp = json.loads(r.text)
        for testcase in testcase_resp["result"]:
            if set(TestCaseParams.items()) == set(TestCaseParams.items()) & set(testcase["TestCaseInfo"].items()):                
                self.TestCaseRecordId = testcase["@rid"]
                print("TestCase already exists. RecordId = " + self.TestCaseRecordId)
                break                
        if self.TestCaseRecordId == "":
            print("Creating new test case...")
            
    def createTestCaseRecord(self):
        TopLvlRecords = dict([("@class","TestCase")])
        TestCaseInfo = {}
        for key, value in self.__dict__.items():            
            if key.find("RecordId") != -1 and value != "":
                if key in ["CardRecordId","Level2RecordId","EcommerceSecurityRecordId","CardSecurityRecordId","TestCaseRecordId"]:
                    continue
                key = re.sub(r'RecordId',"",key)
                if key in ["Tender","Transaction","Interchange"]:
                    key = key + "Data"                    
                TopLvlRecords[key] = value
            elif key.find("RecordId") == -1 and key != "args" and value != "":
                TestCaseInfo[key] = value
        
        if set([]) != set(["3DSecure","AVSData","CVData","IntlAVSData"]) & set(self.args):
            for item in list(set(["3DSecure","AVSData","CVData","IntlAVSData"]) & set(self.args)):
                TestCaseInfo[item] = True
        if "BillPay" in self.args:
            TestCaseInfo["BillPay"] = self.BillPayment
        if "Level2" in self.args:
            TestCaseInfo["Level2"] = self.IsTaxExempt
        TopLvlRecords["TestCaseInfo"] = TestCaseInfo
        
        docURL = "http://localhost:2480/document/" + self.DBname
        headers = {"content-type":"application/json"}
        r = requests.post(docURL, headers=headers, data=json.dumps(TopLvlRecords), auth=HTTPBasicAuth('admin','admin'))
        self.TestCaseRecordId = r.text
        print("New TestCase RecordId = " + self.TestCaseRecordId)
        
    def createNewTestCase(self):
        self.getService()
        self.getCredentials()
        self.getMerchant()
        self.getApplication()
        self.getCardData()
        self.getTenderClasses()
        self.checkForTenderRecord()
        self.getInterchangeData()
        self.getTransactionData()
        self.createTestCaseRecord()
        
    def getTestCaseInfo(self): #For displaying created test cases in GUI, not called from class instance
        clustURL = "http://localhost:2480/cluster/" + globalvars.DBNAME + "/TestCase/100"
        r = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        TestCases = {}
        for record in json.loads(r.text)["result"]:
            text = record["TestCaseInfo"]
            TestCases[record["@rid"]] = text
        return TestCases
    
    def saveMerchantProfile(self): # not called from class instance
        clustURL = "http://localhost:2480/cluster/" + globalvars.DBNAME + "/Merchant/100"
        docURL = "http://localhost:2480/document/" + globalvars.DBNAME + "/"
        r = requests.get(clustURL, auth=HTTPBasicAuth('admin','admin'))
        Merchants = {}
        for record in json.loads(r.text)["result"]:            
            r2 = requests.get(docURL + record["ServiceId"][1:] + "/*:1", auth=HTTPBasicAuth('admin','admin'))
            svc_resp = json.loads(r2.text)
            for skey in svc_resp["ServiceKey"]:
                if skey["MessageType"] == record["MessageType"] and skey["Environment"] == record["Environment"]:
                    record["IdentityToken"] = skey["IdentityToken"]
            record["ServiceId"] = svc_resp["ServiceId"]
            Merchants[record["MerchantProfileId"]] = record
        return Merchants
    
        
    def dataRules(self):    
        #Input Rules
        if self.TenderType not in globalvars.TENDERTYPES:
            print('Invalid Tender Type. Must be one of: "Credit","PINDebit"')
            sys.exit()
        if self.MessageType not in globalvars.MESSAGETYPES:    
            print('Invalid Message Type. Must be one of: "SOAP","REST"')
            sys.exit()
        if self.Host not in globalvars.HOSTNAMES:    
            print('Invalid Host. Must be one of: "EVO HostCap TestHost","EVO TermCap TestHost","EVO HostCap Sandbox","EVO TermCap Sandbox"')
            sys.exit()
        if self.IndustryType not in globalvars.INDUSTRYTYPES:    
            print('Invalid Industry Type. Must be one of: "Retail","Restaurant","MOTO","Ecommerce"')
            sys.exit()
        if self.Workflow not in globalvars.WORKFLOWS:    
            print('Invalid Industry Type. Must be one of: "None","Magensa","ReD"')
            sys.exit()
        if self.Environment not in globalvars.ENVIRONMENTS:    
            print('Invalid Environment. Must be one of: "TEST","CERT","PROD"')
            sys.exit()
        if self.CardType not in globalvars.CARDTYPES:
            print('Invalid Card Type. Must be one of: "Visa","MasterCard","Discover","AmericanExpress"')
            sys.exit()
        #Validate DataBase
        r = requests.get("http://localhost:2480/database/" + self.DBname, auth=HTTPBasicAuth('admin','admin'))
        if r.status_code != 200:
            print("Database not online, or invalid DBname provided.")
            sys.exit()
        #Level2Data Rules    
        if self.IndustryType == "Restaurant" and "Level2" in self.args:
            print("No Level2 for IndustryType: Restaurant")
            sys.exit()
        Level2Args = set(globalvars.LEVEL2ARGS)
        if "Level2" in self.args and not list(Level2Args & set(self.args)):
            print('No arguments found for Level2. Must delcare "Exempt" or "NotExempt"')
            sys.exit()
        if "Level2" in self.args and len(list(Level2Args & set(self.args))) > 1:
            print('Too Many arguments for Level2 found in args. Exactly 1 required.')
            sys.exit()
        #CVData, AVSData, BillPay, Rules
        TenderArgs = set(["CVData","AVSData","IntlAVSData","BillPay"])    
        if list(TenderArgs & set(self.args)) and self.IndustryType in ["Retail","Restaurant"]:
            print("No " + ",".join([str(i) for i in TenderArgs]) + ", for IndustryType: " + self.IndustryType)
            sys.exit()
        BillPayArgs = set(globalvars.BILLPAYARGS)
        if "BillPay" in self.args and not list(BillPayArgs & set(self.args)):    
            print('No argument found for BillPay. Must declare "Recurring" or "Installment"')
            sys.exit()
        if "BillPay" in self.args and len(list(BillPayArgs & set(self.args))) > 1:
            print('Too Many arguments for BillPay found in args. Exactly 1 required.')
            sys.exit()
        #3DSecure Rules    
        if "3DSecure" in self.args and self.IndustryType != "Ecommerce":
            print("No 3DSecure for IndustryType: " + self.IndustryType + ". 3DSecure is only for IndustryType: Ecommerce")
            sys.exit()        
        #PINDebit Rule
        if self.TenderType == "PINDebit" and self.IndustryType in ["MOTO","Ecommerce"]:
            print("No PINDebit for IndustryType: " + self.IndustryType + ". PINDebit is only for IndustryTypes: Retail, Restaurant")
            sys.exit()
        #Magensa Rule
        if self.Workflow == "Magensa" and self.IndustryType in ["MOTO","Ecommerce"]:    
            print("No Magensa for IndustryType: " + self.IndustryType + ". Magensa is only for IndustryTypes: Retail, Restaurant")
            sys.exit()
            
class MerchantSelectFrame(tk.Frame):    
    def __init__(self,master=None,**possiblemerchants):        
        tk.Frame.__init__(self, master)
        self.grid()
        self.popup_frame = tk.Toplevel(height=400,width=400)                       
        #self.popup_frame = tk.Frame(self,height=400,width=400)
        #self.popup_frame.grid(row=0,column=0)
        #self.popup_frame.grid_propagate(0)
        self.DBname = globalvars.DBNAME        
        self.possiblemerchants = possiblemerchants        
        
        self.createVariables()
        self.createWidgets()
        
    def createVariables(self):
        self.merch_menuvar = tk.StringVar()
        self.merch_menuvar.set("Select MerchantProfileId")
        self.merch_menuitemvar = tk.StringVar()
        
        self.merchtextid = tk.IntVar()
        
    def createWidgets(self):        
        self.message_label = tk.Label(self.popup_frame,text="Multiple Merchants found for given inputs.")
        self.message_label.grid(sticky=tk.N,row=0,column=0)
        
        self.merch_menubutton = tk.Menubutton(self.popup_frame,relief="raised",textvariable = self.merch_menuvar)
        self.merch_menubutton.grid(sticky=tk.NW,row=1,column=0)
        self.merch_menu = tk.Menu(self.merch_menubutton)
        self.merch_menubutton["menu"] = self.merch_menu
        for merchant in self.possiblemerchants.keys():
            self.merch_menu.add_checkbutton(label=merchant,variable=self.merch_menuitemvar,onvalue=merchant,command=self.updateMerchantButton)
        
        self.selectmerch_button = tk.Button(self.popup_frame,text="Select Merchant",state="disabled",command=self.selectMerchant)
        self.selectmerch_button.grid(sticky=tk.NW,row=1,column=1)
            
        self.record_canvas = tk.Canvas(self.popup_frame,relief=tk.RIDGE, bd=2,height=400)
        
    def updateMerchantButton(self):
        self.merch_menuvar.set(self.merch_menuitemvar.get())
        if self.merchtextid != 0:
            self.record_canvas.itemconfigure(self.merchtextid,text="")
        self.merchtextid = self.record_canvas.create_text(5,5,anchor=tk.NW,text=self.getRecordText(self.possiblemerchants[self.merch_menuvar.get()]))
        self.record_canvas.grid(sticky=tk.NW,row=2,column=0,columnspan=2)
        self.selectmerch_button["state"] = "active"
        
    def getRecordText(self,recordId):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"        
        r = requests.get(docURL + recordId[1:], auth=HTTPBasicAuth('admin','admin'))        
        self.rectext = json.dumps(json.loads(r.text),sort_keys=True, indent=2, separators =(',',':'))     
        return self.rectext
    
    def selectMerchant(self):
        self.rectext = json.loads(self.rectext)
        print("Selected Merchant: " + self.merch_menuvar.get())        
        self.popup_frame.destroy()       
        self.quit()
        
        
         
    