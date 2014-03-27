import json
import requests
import re
from requests.auth import HTTPBasicAuth
import sys
import os
from globalvars import globalvars


class Database:
    
    def __init__(self):
        #Gets list of classes already created in DB, minus the OrientDB default classes
        self.DBname = globalvars.DBNAME
        self.ClassNames = []
        excludedclasses = ["OFunction","OGraphEdge","OIdentity","OGraphVertex","ORIDs","ORestricted","ORole","OUser","_version"]        
        dbURL = "http://localhost:2480/database/" + self.DBname
        r = requests.get(dbURL, auth=HTTPBasicAuth('admin','admin'))
        db_resp = json.loads(r.text)
        for record in db_resp["classes"]:
            if record["name"] not in excludedclasses:
                self.ClassNames.append(record["name"])
            else:
                continue
        print(self.ClassNames)        
        
        data_files = os.path.join(os.path.dirname( __file__ ), '..', 'GUIs/data_files')
        self.RecordFile = os.path.abspath(os.path.join(data_files,"DataPop.txt"))
        self.PropertyFile = os.path.abspath(os.path.join(data_files,"class_Properties.txt"))
        self.NewRecordFile = os.path.abspath(os.path.join(data_files,"NewRecords.txt"))
        self.MapFile = os.path.abspath(os.path.join(data_files,"MappingData.txt"))        
              
        self.DataExists = {} #Map of Class names with number of records for each class before adding new records
        self.LinkMap = {} #Map of Top Level RecordIds with related linked RecordIds        
    
    def createClass(self):
        propertyfile = open(self.PropertyFile, 'r')
        for line in propertyfile:
            linegroup = line.split('|')
            if linegroup[0] not in self.ClassNames:
                URL = "http://localhost:2480/class/" + self.DBname + "/" + linegroup[0]
                r = requests.post(URL, auth=HTTPBasicAuth('admin','admin'))
                print("Created class " + linegroup[0])
                self.ClassNames.append(linegroup[0])
            else:
                continue
        propertyfile.close()
    
    def createClassProperties(self):        
        propertyfile = open(self.PropertyFile, 'r')
        for line in propertyfile:            
            linegroup = line.split('|')
            propsexist = False
            classURL = "http://localhost:2480/class/" + self.DBname + "/" + linegroup[0]
            r1 = requests.get(classURL, auth=HTTPBasicAuth('admin','admin'))
            class_resp = json.loads(r1.text)
            if "properties" in class_resp.keys():
                propsexist = True
            if linegroup[0] in self.ClassNames and not propsexist:
                propURL = "http://localhost:2480/property/" + self.DBname + "/" + linegroup[0]
                payload = linegroup[1]
                headers = {"content-type":"application/json"}
                r2 = requests.post(propURL, data=payload, headers=headers, auth=HTTPBasicAuth('admin','admin'))
                print("Created " + r2.text + " new properties for class " + linegroup[0])
            else:
                continue
        propertyfile.close()
    
    #Add a new property to an existing class. new_properties is a list of strings like "name=type=linkedclass" 
    #where name == is name of the property being created 
    #and type == type of field (LINK, STRING, EMBEDDEDLIST, etc). if type == LINKLIST or LINK, linkedclass must be included in the new_properties string    
    def addProperty(self, classname, new_properties):    
        classURL = "http://localhost:2480/class/" + self.DBname + "/" + classname
        propURL = "http://localhost:2480/property/" + self.DBname + "/" + classname
        payload = ""
        headers = {"content-type":"application/json"}
        r1 = requests.get(classURL, auth=HTTPBasicAuth('admin','admin'))
        class_resp = json.loads(r1.text)
        if "properties" not in class_resp.keys():
            print("No properties exist currently for this class. Please create using createClassProperties()")
            return
        
        propexists = False
        NameTypePair = new_properties.split('=')
        for record in class_resp["properties"]:                
            if record["name"] == NameTypePair[0]:
                propexists = True
        if propexists == False:            
            if NameTypePair[1].find("LINK") == -1:
                payload = '{"' + NameTypePair[0] + '":{"propertyType":"' + NameTypePair[1] + '"}}'
            elif NameTypePair[1].find("LINK") != -1:    
                payload = '{"' + NameTypePair[0] + '":{"propertyType":"' + NameTypePair[1] + '","linkedClass":"' + NameTypePair[2] + '"}}'
            r2 = requests.post(propURL, data=payload, headers=headers, auth=HTTPBasicAuth('admin','admin'))    
            print("Property type, " + NameTypePair[1] + " was created, with name: " + NameTypePair[0] + ", for class: " + classname)
        else:
            print("Property: " + NameTypePair[0] + " already exists for class: " + classname)
                    
    def checkDataExists(self):
        ExistsMap = {}
        self.FileInd = "master"
        for name in self.ClassNames:
            URL = "http://localhost:2480/class/" + self.DBname + "/" + name
            r = requests.get(URL, auth=HTTPBasicAuth('admin','admin'))            
            ExistsMap[name] = json.loads(r.text)["records"]
            if ExistsMap[name] > 0:
                self.FileInd = "new"
        self.DataExists = ExistsMap
    
    def addRecords(self):
        self.checkDataExists()
        File = ""
        accesstype = ""
        if self.FileInd == "master":
            File = self.RecordFile
            accesstype = "r"
        elif self.FileInd == "new":
            File = self.NewRecordFile
            accesstype = "r+"
        datafile = open(File, accesstype, encoding="utf-8")
        
        docURL = "http://localhost:2480/document/" +self.DBname
        headers = {"content-type":"application/json"}
        linkind = []
        for line in datafile:
            if line != "\n":
                linegroup = line.split('|')
                if File == self.RecordFile and self.DataExists[linegroup[0]] == 0:                
                    payload = linegroup[1]        
                    r2 = requests.post(docURL, data=payload, headers=headers, auth=HTTPBasicAuth('admin','admin'))
                    print("Record of class " + linegroup[0] + " added to database")                     
                elif File == self.NewRecordFile:    
                    masterfile = open(self.RecordFile, 'a', encoding="utf-8")
                    payload = linegroup[1]    
                    r2 = requests.post(docURL, data=payload, headers=headers, auth=HTTPBasicAuth('admin','admin'))
                    print("Record of class " + linegroup[0] + " added to database")
                    masterfile.write(linegroup[0] + "|" + payload)
                    print("New Record copied to master data file")
                    masterfile.close()
                    if linegroup[0] not in linkind and linegroup[0] in ["Service","Credentials","Merchant","Application"]:
                        linkind.append(linegroup[0]) 
                
        
        if self.FileInd == "new":
            datafile.seek(0,0)
            datafile.truncate()
            print("Truncated Records in New Data File")
        datafile.close()
        
        if len(linkind) > 0:
            self.startlinkframe = True
            self.addMapRows(linkind)            
        else:
            self.startlinkframe = False
            
    def addMapRows(self,linkind):
        mapfile = open(self.MapFile, 'r')
        currmaprows = []
        for line in mapfile:        #Creates a list Ids
            line = json.loads(line)            
            currmaprows.append(line["Id"])
        
        linkchoices = {}
        recstolink = {}            
        for classname in linkind:
            url = "http://localhost:2480/query/" + self.DBname + "/sql/select from " + classname + " where @version = 0"
            r = requests.get(url,auth=HTTPBasicAuth('admin','admin'))
            new_recs = json.loads(r.text)["result"]
            
            mapid = ""
            maplinkid = ""
            mapclassid = ""
            if classname == "Service":
                mapid = "ServiceId"
                maplinkid = "ServiceKey"
                mapclassid = "Credentials"
            elif classname == "Credentials":
                mapid = "ServiceKey"
                maplinkid = "ServiceId"
                mapclassid = "Service"
            elif classname == "Merchant":
                mapid = "MerchantProfileId"
                maplinkid = "ServiceId"
                mapclassid = "Service"
            elif classname == "Application":
                mapid = "ApplicationProfileId"
                maplinkid = "ServiceKey"
                mapclassid = "Credentials"            
            
            url2 = "http://localhost:2480/query/" + self.DBname + "/sql/select from " + mapclassid
            if mapclassid not in linkchoices.keys():
                linkchoiceval = []
                r2 = requests.get(url2,auth=HTTPBasicAuth('admin','admin'))
                for record in json.loads(r2.text)["result"]:
                    linkchoiceval.append([record["@rid"],record[maplinkid]])
                linkchoices[classname] = linkchoiceval  # dict with classname and records appropriate to link to. Ie. ServiceKey:<Records of ServiceId>         
            
            recstolinkval = []      
            for record in new_recs:
                if record[mapid] not in currmaprows:
                    recstolinkval.append([record["@rid"],record[mapid]])
            recstolink[classname] = recstolinkval
                    
        self.recstolink = recstolink
        self.linkchoices = linkchoices               
            

    def createLinkMap(self):        
        mapfile = open(self.MapFile, 'r')    #Creates hashmap for data relationships - with id and related ids eg. "2601",:["6B2866C8FD500001"]        
        datamap = {}
        for line in mapfile:
            json_entry = json.loads(line)
            datamap[json_entry["Id"]] = json_entry["MapList"]
        mapfile.close()    
        
        URL = "http://localhost:2480/cluster/" + self.DBname + "/"
        
        IdMap = {}
        for classname in ["Service","Credentials","Merchant","Application"]:              # Creates hashmap for key id vs. record id eg. 'Merchant1':'12:3'
            r = requests.get(URL + classname + "/100", auth=HTTPBasicAuth('admin','admin'))
            json_resp = json.loads(r.text)
            if classname == "Service":
                Id = "ServiceId"
            elif classname == "Credentials":
                Id = "ServiceKey"
            elif classname == "Merchant":
                Id = "MerchantProfileId"
            elif classname == "Application":
                Id = "ApplicationProfileId"    
            else:
                continue
            for record in json_resp["result"]:            
                try:
                    if Id in record:
                        IdMap[record[Id]] = record["@rid"]
                except:
                    continue
            
                             
        Map = {}                            #Creates relational record id hashmap
        for Id, List in datamap.items():
            if len(List) > 1:            
                rids = []
                for item in List:
                    rids.append(IdMap[item])
                Map[IdMap[Id]] = rids    
            else:            
                Map[IdMap[Id]] = IdMap[List[0]]
                
        self.LinkMap = Map    
        
    def updateRecordLinks(self):
        self.createLinkMap()
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        classURL = "http://localhost:2480/class/" + self.DBname + "/"
        headers = {"content-type":"application/json"}
        param = {"updateMode":"partial"}
        for RecordId, RelatedRecords in self.LinkMap.items():
            # Gets recordId from current record then loads record into memory
            RecordId = re.sub(r'#',"",RecordId)
            r = requests.get(docURL + RecordId, auth=HTTPBasicAuth('admin','admin'))
            record_resp = json.loads(r.text)
            
            # Gets field name and type from link/linklist properties then updates record with related record ids
            r = requests.get(url = classURL + record_resp["@class"], auth=HTTPBasicAuth('admin','admin'))
            class_resp = json.loads(r.text)            
            updated = False
            for property in class_resp["properties"]:                
                if property["type"].find("LINK") != -1 and property["name"] not in record_resp.keys(): #If new row was added in map file, add the links to the record                   
                    if property["type"].find("LIST") != -1 and type(RelatedRecords) is str:
                        record_resp[property["name"]] = list([RelatedRecords]) # This is ensuring that when a Service or Credential record has only a single link in the linklist, there is no type error in updating the record
                    else:
                        record_resp[property["name"]] = RelatedRecords
                    updated = True    
                elif property["type"] == "LINKLIST" and property["name"] in record_resp.keys(): #If a new link was added to a linklist in mapfile eg: New Service to ServiceKey, or a link was changed eg: changed MerchantProfile to different ServiceKey, add/change those links in record
                    if type(RelatedRecords) is str:
                        RelatedRecords = list([RelatedRecords])
                    if set(RelatedRecords) != set(record_resp[property["name"]]) & set(RelatedRecords):                        
                        record_resp[property["name"]] = RelatedRecords
                        updated = True
                else:                    
                    continue                    
                    
            if updated == True:                       
                r = requests.put(url = docURL + RecordId, params=param, headers=headers, data=json.dumps(record_resp), auth=HTTPBasicAuth('admin','admin'))
                if r.status_code == 200:                
                    print("Updated record " + RecordId + " with related record links ")
                else:
                    print("An Error occurred updating record " + RecordId + ".\n" + r.text + "\nURL= " + r.url + "\nContent= " + r.request.body)  
            else:
                continue
        
    #kwargs input as key=val where key is field name and val is data value
    def updateRecord(self,RecordId,**kwargs):
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        headers = {"content-type":"application/json"}
        param = {"updateMode":"partial"}
        r1 = requests.get(docURL + RecordId, auth=HTTPBasicAuth('admin','admin'))
        doc_resp = json.loads(r1.text)
        
        #Get List of all possible field names of Record
        r2 = requests.get(url="http://localhost:2480/class/" + self.DBname + "/" + doc_resp["@class"], auth=HTTPBasicAuth('admin','admin'))
        class_resp = json.loads(r2.text)
        FieldNames = []
        for property in class_resp["properties"]:
            FieldNames.append(property["name"])
        
        #Update data in record if property exists for given field name
        for key, val in kwargs.items():
            if key in FieldNames:
                doc_resp[key] = val
            else:
                print("No Field Name: " + key + " in class: " + doc_resp["@class"] + ". Add a new property or check accuracy of input data.")
                sys.exit()    
        r3 = requests.put(url = docURL + RecordId, params=param, headers=headers, data=json.dumps(doc_resp), auth=HTTPBasicAuth('admin','admin'))
        print(r3.text)
        
                
        
    # method dumps class properties into the self.PropertyFile. each class will have a single line in the file, listing all class properties            
    def dumpProperties(self):
        propertyfile = open(self.PropertyFile, 'w')
        classURL = "http://localhost:2480/class/" + self.DBname + "/"
        for classname in self.ClassNames:
            PropString = {}
            r = requests.get(classURL + classname, auth=HTTPBasicAuth('admin','admin'))
            class_resp = json.loads(r.text)
            for property in class_resp["properties"]:
                if property["type"].find("LINK") == -1:
                    PropString[property["name"]] = dict([("propertyType",property["type"])])
                else:
                    PropString[property["name"]] = dict([("propertyType",property["type"]),("linkedClass",property["linkedClass"])])
            propertyfile.write(classname + "|" + json.dumps(PropString) +"\n")
        propertyfile.close()    
    
    def dumpRecords(self):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/"
        datafile = open(self.RecordFile, 'w')
        for classname in self.ClassNames:
            if classname not in ["TenderData","TestCase"]: #Only base records, not link records
                r = requests.get(clustURL + classname +"/1000", auth=HTTPBasicAuth('admin','admin'))
                clust_resp = json.loads(r.text)
                for record in clust_resp["result"]:
                    delkeys = []
                    for key, val in record.items():                        
                        if type(val) is list:
                            if re.match(r'\#\d+\:\d+', val[0]) != None:
                                delkeys.append(key)
                        else:                            
                            if re.match(r'\#\d+\:\d+', str(val)) != None:
                                delkeys.append(key)
                    for key in delkeys:
                        del record[key]
                    del record["@type"]                    
                    del record["@version"]                               
                    datafile.write(classname + "|" + json.dumps(record) + "\n")
        datafile.close()            
            
    def populateData(self):
        self.addRecords()
        self.createLinkMap()
        if self.DataExists["Service"] + self.DataExists["Credentials"] + self.DataExists["Application"] + self.DataExists["Merchant"] != len(self.LinkMap.keys()):
            self.updateRecordLinks()
            
    def getCluster(self, classname):
        clustURL = "http://localhost:2480/cluster/" + self.DBname + "/"
        r = requests.get(clustURL + classname +"/100", auth=HTTPBasicAuth('admin','admin'))
        clust_resp = json.loads(r.text)
        return clust_resp
    
    def getRecord(self,recordId,extend):            
        docURL = "http://localhost:2480/document/" + self.DBname + "/"
        fetchplan = ""        
        if extend == 1:
            fetchplan = "/*:1"
        r = requests.get(docURL + recordId[1:]+ fetchplan, auth=HTTPBasicAuth('admin','admin'))        
        rectext = json.dumps(json.loads(r.text),sort_keys=True, indent=2, separators =(',',':'))     
        return rectext
    
    def queryRecords(self,classname,param):
        param = param.split("=")
        url = "http://localhost:2480/query/" + self.DBname + "/sql/select from " +classname + " where " + param[0] + " = '" + param[1] + "'"
        r = requests.get(url,auth=HTTPBasicAuth('admin','admin'))
        if r.status_code != 200:
            return "Bad query. Try again"
        else:
            querytext = json.dumps(json.loads(r.text),sort_keys=True, indent=2, separators =(',',':'))
            return querytext
        
    def deleteRecord(self,recordid,classname): #Deletes, record itself, relations in the mapfile, and any test cases containing a link to the deleted record
        url = "http://localhost:2480/document/" + self.DBname + "/"
        clusturl = "http://localhost:2480/query/" + self.DBname + "/sql/select from TestCase where any() traverse ( @rid = '"+ recordid[1:] + "' )"
        messages = []
        
        if classname != "TestCase":
            c = requests.get(clusturl, auth=HTTPBasicAuth('admin','admin')) #get TestCase records that contain the record to delete
            for testcase in json.loads(c.text)["result"]:
                requests.delete(url + testcase["@rid"][1:],auth=HTTPBasicAuth('admin','admin')) #Deletes each test case containing record to delete
                messages.append("Deleted TestCase record " + testcase["@rid"] + " -- contained link to deleted record: " + recordid)
         
        r = requests.get(url + recordid[1:], auth=HTTPBasicAuth('admin','admin'))
        requests.delete(url + recordid[1:],auth=HTTPBasicAuth('admin','admin')) #Delete actual record
        if classname in ["Service","Credentials","Application","Merchant"]:
            Id = ""
            mapkey = ""
            if classname == "Service":
                Id = "ServiceId"
                mapkey = "Svc"
            elif classname == "Credentials":
                Id = "ServiceKey"
                mapkey = "SK"
            elif classname == "Merchant":
                Id = "MerchantProfileId"
            elif classname == "Application":
                Id = "ApplicationProfileId"            
            file = open(self.MapFile,"r")
            maplines = file.readlines()
            
            delrow = 0
            delind = False                                    
            for i,line in enumerate(maplines): #Find and delete mapfile row matching Id of the deleted record
                if json.loads(r.text)[Id] == json.loads(line)["Id"]:
                    delrow = i
                    delind = True
                    break            
            if delind == True: #So as to not delete row 0 if loop does not find an Id match
                del maplines[delrow]
                messages.append("Removed row from mapfile corresponding to deleted record: " + recordid)            
            
            for i,line in enumerate(maplines): #If a Service or Credential record was deleted, erase that Id from the respective mapfile row
                if mapkey != "":
                    if json.loads(r.text)[Id] in json.loads(line)["MapList"]:
                        messages.append("Removed reference to " + json.loads(r.text)[Id] + " in row Id=" + json.loads(line)["Id"] + " of mapfile")
                        del json.loads(line)["MapList"][json.loads(line)["MapList"].index(json.loads(r.text)[Id])] # this statement is equivalent to - del MapList[i] - finds index of Id in MapList then deletes it from the list                        
                        
                                    
            file.close()
            file = open(self.MapFile,"w")
            file.writelines(maplines)
            file.close()
        return messages
                    
         

        