import tkinter as tk
import json
import requests
import re
from requests.auth import HTTPBasicAuth
from automation import datacreate
import csv
import os


class RegressionGui(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self, master)
        self.grid()        
        self.main_frame = tk.Frame(self,height=400,width=400)
        self.main_frame.grid(row=0,column=0)
        
        self.createVariables()
        self.createWidgets()
        self.getTestCases()
        
    def createVariables(self):
        self.dbname_var = tk.StringVar()
        self.dbname_var.set("CWSData")
        
        self.envselect_menuvar = tk.StringVar()
        self.envselect_menuvar.set("Select Environment")        
        self.envselect_menuitemvar = tk.StringVar()
        
        self.messagetype_menuvar = tk.StringVar()
        self.messagetype_menuvar.set("Select Message Type")        
        self.messagetype_menuitemvar = tk.StringVar()
        
        self.hosttype_menuvar = tk.StringVar()
        self.hosttype_menuvar.set("Select Host")        
        self.hosttype_menuitemvar = tk.StringVar()
        
        self.tcdisp_var = tk.StringVar()
        
        self.create_messagevar = tk.StringVar()
        
    def createWidgets(self):
        self.dbname_entry = tk.Entry(self.main_frame,textvariable=self.dbname_var)
        self.dbname_entry.grid(sticky=tk.N,row=0,column=0,columnspan=3)
        
        self.refresh_button = tk.Button(self.main_frame,text="Refresh Data",command=self.getTestCases)
        self.refresh_button.grid(sticky=tk.NW,row=0,column=2)
        
        self.envselect_menubutton = tk.Menubutton(self.main_frame,relief="raised",textvariable=self.envselect_menuvar,state="active")
        self.envselect_menubutton.grid(sticky=tk.NW,row=1,column=0)
        self.envselect_menu = tk.Menu(self.envselect_menubutton)
        self.envselect_menubutton["menu"] = self.envselect_menu
        for item in ["TEST","CERT","PROD"]:
            self.envselect_menu.add_checkbutton(label=item,variable=self.envselect_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("envselect"))
        
        self.messagetype_menubutton = tk.Menubutton(self.main_frame,relief="raised",textvariable=self.messagetype_menuvar,state="active")
        self.messagetype_menubutton.grid(sticky=tk.NW,row=1,column=1)
        self.messagetype_menu = tk.Menu(self.messagetype_menubutton)
        self.messagetype_menubutton["menu"] = self.messagetype_menu
        for item in ["SOAP","REST"]:
            self.messagetype_menu.add_checkbutton(label=item,variable=self.messagetype_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("messagetype"))
        
        self.hosttype_menubutton = tk.Menubutton(self.main_frame,relief="raised",textvariable=self.hosttype_menuvar,state="active")
        self.hosttype_menubutton.grid(sticky=tk.NW,row=1,column=2)
        self.hosttype_menu = tk.Menu(self.hosttype_menubutton)
        self.hosttype_menubutton["menu"] = self.hosttype_menu
        for item in ["EVO HostCap TestHost","EVO TermCap TestHost","EVO HostCap Sandbox","EVO TermCap Sandbox","EVO TermCap AutoResponder","EVO TermCap TPS","EVO HostCap TPS"]:
            self.hosttype_menu.add_checkbutton(label=item,variable=self.hosttype_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("hosttype"))
        
        self.tcdisp_scroll = tk.Scrollbar(self.main_frame,orient=tk.VERTICAL)
        self.tcdisp_scroll.grid(sticky=tk.N+tk.S,row=2,column=3)
        self.tcdisp_listbox = tk.Listbox(self.main_frame,width=60,listvariable=self.tcdisp_var,activestyle="dotbox")
        self.tcdisp_listbox.grid(sticky=tk.NW,row=2,column=0,columnspan=3)
        self.tcdisp_scroll["command"] = self.tcdisp_listbox.yview
        
        self.datasource_button = tk.Button(self.main_frame,text="Create Regression DataSource",command=self.createDataSource)
        self.create_message = tk.Message(self.main_frame, textvariable=self.create_messagevar,aspect=1100)
    
    def getTestCases(self):
        URL = "http://localhost:2480/cluster/" + self.dbname_var.get() + "/TestCase/100"
        r = requests.get(URL, auth=HTTPBasicAuth('admin','admin'))
        self.testcases = json.loads(r.text)
        
    def updateButton(self,varname):
        menuvar = varname + "_menuvar"
        menuitemvar = varname + "_menuitemvar"
        self.__dict__[menuvar].set(self.__dict__[menuitemvar].get())
        self.displayTestCases()        
        
        
    def displayTestCases(self):        
        if self.envselect_menuitemvar.get() == "":
            self.tcdisp_var.set("Must_Select_Environment!")
        else:
            self.getTCSubSet(self.envselect_menuitemvar.get(),self.messagetype_menuitemvar.get(),self.hosttype_menuitemvar.get())            
            tempstr = ""
            for info in self.tcset.values():
                tempstr = tempstr + info["MessageType"] + "-" + re.sub(r" ","-",info["Host"]) + "-" + info["IndustryType"] + "-" + info["CardType"] + " "
            self.tcdisp_var.set(tempstr)
            self.datasource_button.grid(sticky=tk.N,row=3,column=0,columnspan=4)
            self.create_message.grid_forget()           
            
                    
    def getTCSubSet(self,env,*args):        
        self.tcset = {}
        if args[0] == "" and args[1] == "":
            for record in self.testcases["result"]:                            
                if record["TestCaseInfo"]["Environment"] == env:
                    self.tcset[record["@rid"]] = record["TestCaseInfo"]
        if args[0] != "" and args[1] == "":
            for record in self.testcases["result"]:                            
                if record["TestCaseInfo"]["Environment"] == env and record["TestCaseInfo"]["MessageType"] == args[0]:
                    self.tcset[record["@rid"]] = record["TestCaseInfo"]
        if args[0] == "" and args[1] != "":
            for record in self.testcases["result"]:                            
                if record["TestCaseInfo"]["Environment"] == env and record["TestCaseInfo"]["Host"] == args[1]:
                    self.tcset[record["@rid"]] = record["TestCaseInfo"]
        if args[0] != "" and args[1] != "":
            for record in self.testcases["result"]:                            
                if record["TestCaseInfo"]["Environment"] == env and record["TestCaseInfo"]["MessageType"] == args[0] and record["TestCaseInfo"]["Host"] == args[1]:
                    self.tcset[record["@rid"]] = record["TestCaseInfo"]
                    
    def createDataSource(self):
        if self.messagetype_menuitemvar.get() != "" and self.envselect_menuitemvar.get() != "":
            dscolnames = []
            classnames = set(datacreate.Database(self.dbname_var.get()).ClassNames) - set(["TestCase,TenderData"])
            for name in list(classnames):
                r = requests.get("http://localhost:2480/class/" + self.dbname_var.get() + "/" + name,auth=HTTPBasicAuth('admin','admin'))
                for prop in json.loads(r.text)["properties"]:
                    if prop["type"] == "STRING" or prop["type"] == "INTEGER":
                        dscolnames.append(name + ":" + prop["name"])            
            dscolnames = list(set(dscolnames))          
            dscolnames.extend(["CardSecurityData:PostalCode","CardSecurityData:Street","Level2Data:Amount","Level2Data:IsTaxExempt","Level2Data:TaxExemptNumber"])
            
            self.datadict = {}
            for name in dscolnames:
                self.datadict[name] = []
            
            for i,tcrid in enumerate(self.tcset.keys()):
                r = requests.get("http://localhost:2480/document/" + self.dbname_var.get() + "/" + tcrid[1:] + "/*:2",auth=HTTPBasicAuth('admin','admin'))            
                self.getFields(json.loads(r.text), i)
                for val in self.datadict.values():
                    if len(val) == i:
                        val.append("")
                self.performDataRules(tcrid,i)            
            self.createCSV()
            self.create_message.grid(sticky=tk.N,row=4,column=0,columnspan=4)
            self.create_messagevar.set("Data Source Created")
        else:
            self.create_message.grid(sticky=tk.N,row=4,column=0,columnspan=4)
            self.create_messagevar.set("Must Select Environment and Message Type!")
                
    
    def getFields(self,tcrecord, index):
        label = tcrecord["@class"]        
        for key,val in tcrecord.items():
            if type(val) is str: 
                if key[:1] != "@" and val[:1] != "#":                    
                    if len(self.datadict[label + ":" + key]) == index:
                        self.datadict[label + ":" + key].append(val)
            elif type(val) is dict and key != "TestCaseInfo":
                self.getFields(val, index)
                
    def performDataRules(self,tcrid,index):
        if self.tcset[tcrid]["EntryMode"] == "TrackDataFromMSR":
            self.datadict["CardData:Expire"][index] = ""
            self.datadict["CardData:PAN"][index] = ""
        else:
            self.datadict["CardData:Track2Data"][index] = ""
        if "BillPay" in self.tcset[tcrid].keys():
            self.datadict["TransactionData:CustomerPresent"] = "BillPayment"
            
    def createCSV(self):
        data_files = os.path.join(os.path.dirname( __file__ ), 'data_files')
        DataCSVFile = os.path.abspath(os.path.join(data_files,"RegressionData.csv"))        
        regrcsv = open(DataCSVFile, "w")
        rowwriter = csv.writer(regrcsv,delimiter=",",lineterminator='\n')
        rowwriter.writerow(list(self.datadict.keys()))
        for row in zip(*list(self.datadict.values())):
            rowwriter.writerow(row)
        regrcsv.close()              

regframe = RegressionGui()
regframe.master.title("Regression Plan")
regframe.mainloop()