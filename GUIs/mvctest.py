import abc
import requests
import json
from globalvars import globalvars
from requests.auth import HTTPBasicAuth

class CWSDataQuery(object):
    __metaclass__ = abc.ABCMeta    
        
    @abc.abstractmethod
    def getRecord(self):
        pass
        #Abstract Method for querying OrientDB for data
        
    @abc.abstractmethod
    def buildQueryString(self):
        pass
        
    @property
    @abc.abstractmethod       
    def recordid(self):
        pass
        #Abstract property for recordid
        
    @property
    @abc.abstractmethod       
    def classkey(self):
        pass
        #Abstract property for class specific keys - eg. ServiceId, ServiceKey   
    
    @classmethod
    def __subclasshook__(cls,C):
        if cls is CWSDataQuery:
            if hasattr(C,"getRecord"):
                return True
        return NotImplemented
            
class Service(CWSDataQuery):    
            
    def getRecord(self,Host,Workflow):
        url = "http://localhost:2480/query/" + globalvars.DBNAME + "/sql/select from Service where Host = '" + Host + "' and Workflow = '" + Workflow + "'"
        r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
        svc_resp = json.loads(r1.text)
        self._recordid = svc_resp["result"][0]["@rid"]
        self.ServiceId = svc_resp["result"][0]["ServiceId"]
    
    @property  
    def recordid(self):
        return self._recordid
    
    @property  
    def classkey(self):
        return self.ServiceId
    
class Credentials(CWSDataQuery):
    def getRecord(self,Environment,MessageType,ServiceId):
        url = "http://localhost:2480/query/" + globalvars.DBNAME + "/sql/select from Credentials where Environment = '" + Environment + "' and ServiceId contains '" + ServiceId + "' and MessageType = '" + self.MessageType + "'"
        r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
        cred_resp = json.loads(r1.text)
        self._recordid = cred_resp["result"][0]["@rid"]
        self.ServiceKey = cred_resp["result"][0]["ServceKey"]
        
    @property    
    def recordid(self):
        return self._recordid
    
    @property  
    def classkey(self):
        return self.ServiceKey
    
class CardData(CWSDataQuery):
    def __init__(self,Environment,CardType):
        self.CardType = CardType
        self.Environment = Environment
         
    def getRecord(self):
        url = "http://localhost:2480/query/" + globalvars.DBNAME + "/sql/select from CardData where Environment = '" + self.Environment + "' and CardType = '" + self.CardType + "'"
        r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
        card_resp = json.loads(r1.text)
        self._recordid = card_resp["result"][0]["@rid"]
        self.PAN = card_resp["result"][0]["PAN"]
        
    def buildQueryString(self):
        return " and any() traverse (CardType = '" + self.CardType + "' and Environment = '" + self.Environment + "')"
    
    @property    
    def recordid(self):
        return self._recordid
    
    @property  
    def classkey(self):
        return self.PAN
        
class CardSecurityData(CWSDataQuery):
    def __init__(self,TenderType,*cardsecargs):
        self.TenderType = TenderType
        self.cardsecargs = cardsecargs
                
    def getRecord(self,PAN):
        url = "http://localhost:2480/query/" + globalvars.DBNAME + "/sql/select from CardSecurityData where PAN = '" + PAN + "' and"
        for arg in globalvars.CARDSECARGS:
            if arg in self.cardsecargs:
                url += arg + " is not null and "
            else:
                url += arg + " is null and "
        if self.TenderType == "PINDebit":
            url += "PIN is not null"
        else:
            url += "PIN is null"
        r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
        cardsec_resp = json.loads(r1.text)
        self._recordid = cardsec_resp["result"][0]["@rid"]
    
    def buildQueryString(self):
        if len(self.cardsecargs) == 0 and self.TenderType != "PINDebit":
            self._recordid = None            
            return "' and CardSecurityData is null "
        query = "' and any() traverse (PAN=$PAN and "        
        for arg in globalvars.CARDSECARGS:
            if arg in self.cardsecargs:
                query += arg + " is not null and "
            else:
                query += arg + " is null and "
        if self.TenderType == "PINDebit":
            query += "PIN is not null)"
        else:
            query += "PIN is null)"
        return query
        
    @property    
    def recordid(self):
        return self._recordid
    
    @property  
    def classkey(self):
        return None

class EcommerceSecurityData(CWSDataQuery):
    def __init__(self,EcommSecureInd):
        self.EcommSecureInd = EcommSecureInd
        
    def getRecord(self,PAN):
        url = "http://localhost:2480/query/" + globalvars.DBNAME + "/sql/select from EcommerceSecurityData where PAN = '" + PAN + "'"
        r1 = requests.get(url, auth=HTTPBasicAuth('admin','admin'))
        ecommsec_resp = json.loads(r1.text)
        self._recordid = ecommsec_resp["result"][0]["@rid"]
        
    def buildQueryString(self):
        if self.EcommSecureInd == None:
            self._recordid = None
            return " and EcommerceSecurityData is null "            
        else:
            return " and EcommerceSecurityData.PAN = $PAN "
        
    @property    
    def recordid(self):
        return self._recordid
    
    @property  
    def classkey(self):
        return None
        
class TenderObject:
    def __init__(self,TenderType,Environment,CardType,EcommSecureInd,*cardsecargs):
        self.card = CardData(Environment,CardType)
        self.cardsec = CardSecurityData(TenderType,*cardsecargs)
        self.ecommsec = EcommerceSecurityData(EcommSecureInd)
        query = "select from TenderData let $PAN = CardData.PAN where TenderType = '" + TenderType + self.cardsec.buildQueryString() + self.ecommsec.buildQueryString() + self.card.buildQueryString()        
        r1 = requests.get("http://localhost:2480/query/" + globalvars.DBNAME + "/sql/" + query,auth=HTTPBasicAuth('admin','admin'))
        if json.loads(r1.text)["result"] == []:
            #self.createTenderRecord()
            print(self.ecommsec.recordid)
        
    def createTenderRecord(self):
        self.card.getRecord()        
        self.cardsec.getRecord(self.card.classkey)
        

TenderObject("Credit","TEST","Visa",None,"AVSData","CVData")


