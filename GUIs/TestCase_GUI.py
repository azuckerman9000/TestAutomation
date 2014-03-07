from automation import testcasebuilder
from automation import soapauthorize
from automation import restjsonauthorize
import tkinter as tk
import re
import json


class TCBuildGui(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self, master)
        self.grid()        
        self.build_frame = tk.Frame(self,height=400,width=400)
        self.build_frame.grid(row=0,column=0)
        #self.build_frame.grid_propagate(0)
        self.createLabels()
        self.createVariables()
        self.createMenus()
        
        self.optionals = OptionalArgsFrame(self)        
        self.optionals.createLabels()
        self.optionals.createVariables()
        self.optionals.createWidgets()
        
        self.tcview = ViewExistingTests(self,self.db_var.get())
        self.tcview.createWidgets()
        self.tcview.showTestCases()
        
        self.mpview = SaveMerchantProfileFrame(self,self.db_var.get())
        self.mpview.createWidgets()
        
        self.createBuildButton()
        self.createReset()
        self.createSOAPReqButton()
        self.createRESTReqButton()
        
    def createLabels(self):
        self.db_label = tk.Label(self.build_frame, text="Database Name:")
        self.db_label.grid(sticky=tk.NW,row=0,column=0)        
        
        self.tender_label = tk.Label(self.build_frame, text="Tender Type:")
        self.tender_label.grid(sticky=tk.NW,row=1,column=0)
        
        self.message_label = tk.Label(self.build_frame, text="Message Type:")
        self.message_label.grid(sticky=tk.NW,row=2,column=0)
        
        self.host_label = tk.Label(self.build_frame, text="Host:")
        self.host_label.grid(sticky=tk.NW,row=3,column=0)
        
        self.industry_label = tk.Label(self.build_frame, text="Industry Type:")
        self.industry_label.grid(sticky=tk.NW,row=4,column=0)
        
        self.workflow_label = tk.Label(self.build_frame, text="Workflow:")
        self.workflow_label.grid(sticky=tk.NW,row=5,column=0)
        
        self.environment_label = tk.Label(self.build_frame, text="Environment:")
        self.environment_label.grid(sticky=tk.NW,row=6,column=0)
        
        self.card_label = tk.Label(self.build_frame, text="Card Type:")
        self.card_label.grid(sticky=tk.NW,row=7,column=0)
        
    def createVariables(self):
        self.db_var = tk.StringVar()
        self.db_var.set("CWSData")        
        
        self.tender_menuvar = tk.StringVar()
        self.tender_menuvar.set("TenderType")
        self.tender_menuitemvar = tk.StringVar()
        
        self.message_menuvar = tk.StringVar()
        self.message_menuvar.set("MessageType")
        self.message_menuitemvar = tk.StringVar()
        
        self.host_menuvar = tk.StringVar()
        self.host_menuvar.set("Host")
        self.host_menuitemvar = tk.StringVar()
        
        self.industry_menuvar = tk.StringVar()
        self.industry_menuvar.set("IndustryType")
        self.industry_menuitemvar = tk.StringVar()
        
        self.workflow_menuvar = tk.StringVar()
        self.workflow_menuvar.set("Workflow")
        self.workflow_menuitemvar = tk.StringVar()
        
        self.environment_menuvar = tk.StringVar()
        self.environment_menuvar.set("Environment")
        self.environment_menuitemvar = tk.StringVar()
        
        self.card_menuvar = tk.StringVar()
        self.card_menuvar.set("CardType")
        self.card_menuitemvar = tk.StringVar()
    
    def createMenus(self):
        self.db_entry = tk.Entry(self.build_frame, textvariable=self.db_var)
        self.db_entry.grid(sticky=tk.NW,row=0,column=1)
        
        self.tender_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.tender_menuvar, state="active")
        self.tender_menubutton.grid(sticky=tk.NW,row=1,column=1)
        self.tender_menu = tk.Menu(self.tender_menubutton)
        self.tender_menubutton["menu"] = self.tender_menu
        for item in ["Credit","PINDebit"]:
            self.tender_menu.add_checkbutton(label=item,variable=self.tender_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("tender"))
            
        self.message_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.message_menuvar, state="active")
        self.message_menubutton.grid(sticky=tk.NW,row=2,column=1)
        self.message_menu = tk.Menu(self.message_menubutton)
        self.message_menubutton["menu"] = self.message_menu
        for item in ["SOAP","REST"]:
            self.message_menu.add_checkbutton(label=item,variable=self.message_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("message"))
        
        self.host_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.host_menuvar, state="active")
        self.host_menubutton.grid(sticky=tk.NW,row=3,column=1)
        self.host_menu = tk.Menu(self.host_menubutton)
        self.host_menubutton["menu"] = self.host_menu
        for item in ["EVO HostCap TestHost","EVO TermCap TestHost","EVO HostCap Sandbox","EVO TermCap Sandbox","EVO TermCap AutoResponder","EVO TermCap TPS","EVO HostCap TPS"]:
            self.host_menu.add_checkbutton(label=item,variable=self.host_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("host"))
            
        self.industry_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.industry_menuvar, state="active")
        self.industry_menubutton.grid(sticky=tk.NW,row=4,column=1)
        self.industry_menu = tk.Menu(self.industry_menubutton)
        self.industry_menubutton["menu"] = self.industry_menu
        for item in ["Retail","Restaurant","Ecommerce","MOTO"]:
            self.industry_menu.add_checkbutton(label=item,variable=self.industry_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("industry"))
            
        self.workflow_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.workflow_menuvar, state="active")
        self.workflow_menubutton.grid(sticky=tk.NW,row=5,column=1)
        self.workflow_menu = tk.Menu(self.workflow_menubutton)
        self.workflow_menubutton["menu"] = self.workflow_menu
        for item in ["Magensa","ReD","None"]:
            self.workflow_menu.add_checkbutton(label=item,variable=self.workflow_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("workflow"))
            
        self.environment_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.environment_menuvar, state="active")
        self.environment_menubutton.grid(sticky=tk.NW,row=6,column=1)
        self.environment_menu = tk.Menu(self.environment_menubutton)
        self.environment_menubutton["menu"] = self.environment_menu
        for item in ["TEST","CERT","PROD"]:
            self.environment_menu.add_checkbutton(label=item,variable=self.environment_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("environment"))
            
        self.card_menubutton = tk.Menubutton(self.build_frame,relief="raised",textvariable=self.card_menuvar, state="active")
        self.card_menubutton.grid(sticky=tk.NW,row=7,column=1)
        self.card_menu = tk.Menu(self.card_menubutton)
        self.card_menubutton["menu"] = self.card_menu
        for item in ["Visa","MasterCard","AmericanExpress","Discover"]:
            self.card_menu.add_checkbutton(label=item,variable=self.card_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("card"))
    
    def updateButton(self,varname):
        menuvar = varname + "_menuvar"
        menuitemvar = varname + "_menuitemvar"
        self.__dict__[menuvar].set(self.__dict__[menuitemvar].get())
    
    def createBuildButton(self):        
        self.buildtxn_button = tk.Button(self, text="Build Transaction", command=self.buildTransaction)
        self.buildtxn_button.grid(sticky=tk.NW,row=2,column=0)
        
        self.buildtxn_messagevar = tk.StringVar()        
        self.buildtxn_message = tk.Message(self,textvariable=self.buildtxn_messagevar,aspect=800)
        self.buildtxn_message.grid(sticky=tk.NW,row=2,column=1)    
        
    def buildTransaction(self):
        self.reqfields = [self.db_var.get(),self.tender_menuitemvar.get(),self.message_menuitemvar.get(),self.host_menuitemvar.get(),self.industry_menuitemvar.get(),self.workflow_menuitemvar.get(),self.environment_menuitemvar.get(),self.card_menuitemvar.get()]
        self.optfields = [self.optionals.cv_var.get(),self.optionals.avs_var.get(),self.optionals.threed_var.get(),self.optionals.level2_menuitemvar.get(),self.optionals.billpay_menuitemvar.get()]
        allfields = True
        for field in self.reqfields:
            if field == "":
                allfields = False
                self.buildtxn_messagevar.set("You must enter all required fields.")                
                break
        if allfields == True:
            args = []                        
            for field in self.optfields:
                if field != "":
                    args.append(field)
                    if field in ["Exempt","NotExempt"]:
                        args.append("Level2")
                    elif field in ["Recurring","Installment"]:
                        args.append("BillPay")             
            self.tc = testcasebuilder.Transaction(self.db_var.get(),self.tender_menuitemvar.get(),self.message_menuitemvar.get(),self.host_menuitemvar.get(),self.industry_menuitemvar.get(),self.workflow_menuitemvar.get(),self.environment_menuitemvar.get(),self.card_menuitemvar.get(), *args)
            self.buildtxn_messagevar.set("Test Case RecordId ="+ self.tc.TestCaseRecordId)
            #self.soapreq_button["state"] = "active"            
            self.tcview.showTestCases() 
    
    def createReset(self):
        self.reset_button = tk.Button(self,text="Reset Fields",command=self.resetFields)
        self.reset_button.grid(sticky=tk.NW,row=3,column=0)
        
    def resetFields(self):
        for varname in ["tender","message","host","industry","workflow","environment","card"]:
            menubutton = varname + "_menubutton"
            menu = varname + "_menu"
            self.__dict__[menubutton].destroy()
            self.__dict__[menu].destroy()
        self.buildtxn_messagevar.set("")
        self.createVariables()
        self.createMenus()
        
        for varname in ["billpay","level2"]:
            menubutton = varname + "_menubutton"
            menu = varname + "_menu"
            self.optionals.__dict__[menubutton].destroy()
            self.optionals.__dict__[menu].destroy()
        for varname in ["cv","avs","threed"]:
            button = varname + "_button"
            self.optionals.__dict__[button].destroy()        
        self.optionals.createVariables()
        self.optionals.createWidgets()            
            
    def createSOAPReqButton(self):
        self.soapreq_button = tk.Button(self,text="Create SOAP Request",state="disabled")#,command=lambda: self.createSOAPReq(self.db_var.get(),self.tc.TestCaseRecordId[1:]))
        self.soapreq_button.grid(sticky=tk.N,row=4,column=0,columnspan=3)
        
        self.soapreq_messagevar = tk.StringVar()
        self.soapreq_message = tk.Message(self,textvariable=self.soapreq_messagevar, aspect=800)
        self.soapreq_message.grid(sticky=tk.NW,row=4,column=3)
        
    def createSOAPReq(self,DBname,RecordId):
        req = soapauthorize.SOAPRequest(DBname,RecordId)
        self.soapreq_messagevar.set("SOAP Request Created for TestCase record = " + RecordId)
        
    def createRESTReqButton(self):
        self.restreq_button = tk.Button(self,text="Create REST Request",state="disabled")#,command=lambda: self.createrestReq(self.db_var.get(),self.tc.TestCaseRecordId[1:]))
        self.restreq_button.grid(sticky=tk.N,row=5,column=0,columnspan=3)
        
        self.restreq_messagevar = tk.StringVar()
        self.restreq_message = tk.Message(self,textvariable=self.restreq_messagevar,aspect=800)
        self.restreq_message.grid(sticky=tk.NW,row=5,column=3)
        
    def createRESTReq(self,DBname,RecordId):
        req = restjsonauthorize.RestJsonRequest(DBname,RecordId)
        self.restreq_messagevar.set("REST Request Created for TestCase record = " + RecordId)

class OptionalArgsFrame:
    def __init__(self,frame):        
        self.optargs_frame = tk.Frame(frame,width=200,height=200)
        self.optargs_frame.grid(row=1,column=0)
        #self.optargs_frame.grid_propagate(0)
        
    def createVariables(self):
        self.cv_var = tk.StringVar()
        
        self.avs_var = tk.StringVar()
        
        self.threed_var = tk.StringVar()
        
        self.level2_menuvar = tk.StringVar()
        self.level2_menuvar.set("IsTaxExempt")
        self.level2_menuitemvar = tk.StringVar()
        
        self.billpay_menuvar = tk.StringVar()
        self.billpay_menuvar.set("BillPayment")
        self.billpay_menuitemvar = tk.StringVar()
        
    def createLabels(self):
        self.title_label = tk.Label(self.optargs_frame, text="Optional Arguments:")
        self.title_label.grid(sticky=tk.NW,row=0,column=0, columnspan=2)
        
        self.cv_label = tk.Label(self.optargs_frame, text="Include CVData:")
        self.cv_label.grid(sticky=tk.NW,row=1,column=0)
        
        self.avs_label = tk.Label(self.optargs_frame, text="Include AVSData:")
        self.avs_label.grid(sticky=tk.NW,row=2,column=0)
        
        self.threed_label = tk.Label(self.optargs_frame, text="Include 3DSecure:")
        self.threed_label.grid(sticky=tk.NW,row=3,column=0)
        
        self.level2_label = tk.Label(self.optargs_frame, text="Include Level2Data:")
        self.level2_label.grid(sticky=tk.NW,row=4,column=0)
        
        self.billpay_label = tk.Label(self.optargs_frame, text="Include BillPayment:")
        self.billpay_label.grid(sticky=tk.NW,row=5,column=0)
        
    def createWidgets(self):
        self.cv_button = tk.Checkbutton(self.optargs_frame,text="CVData",variable=self.cv_var,onvalue="CVData",offvalue="")
        self.cv_button.grid(sticky=tk.NW,row=1,column=1)
        
        self.avs_button = tk.Checkbutton(self.optargs_frame,text="AVSData",variable=self.avs_var,onvalue="AVSData",offvalue="")
        self.avs_button.grid(sticky=tk.NW,row=2,column=1)
        
        self.threed_button = tk.Checkbutton(self.optargs_frame,text="3DSecure",variable=self.threed_var,onvalue="3DSecure",offvalue="")
        self.threed_button.grid(sticky=tk.NW,row=3,column=1)
        
        self.level2_menubutton = tk.Menubutton(self.optargs_frame,relief="raised",textvariable=self.level2_menuvar, state="active")
        self.level2_menubutton.grid(sticky=tk.NW,row=4,column=1)
        self.level2_menu = tk.Menu(self.level2_menubutton)
        self.level2_menubutton["menu"] = self.level2_menu
        for item in ["Exempt","NotExempt"]:
            self.level2_menu.add_checkbutton(label=item,variable=self.level2_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("level2"))
            
        self.billpay_menubutton = tk.Menubutton(self.optargs_frame,relief="raised",textvariable=self.billpay_menuvar, state="active")
        self.billpay_menubutton.grid(sticky=tk.NW,row=5,column=1)
        self.billpay_menu = tk.Menu(self.billpay_menubutton)
        self.billpay_menubutton["menu"] = self.billpay_menu
        for item in ["Recurring","Installment"]:
            self.billpay_menu.add_checkbutton(label=item,variable=self.billpay_menuitemvar,onvalue=item,offvalue="", command=lambda : self.updateButton("billpay"))        
            
    def updateButton(self,varname):
        menuvar = varname + "_menuvar"
        menuitemvar = varname + "_menuitemvar"
        self.__dict__[menuvar].set(self.__dict__[menuitemvar].get())
        
class ViewExistingTests:
    def __init__(self,frame,DBname):
        self.DBname = DBname        
        self.tests_frame = tk.Frame(frame,width=400,height=200)
        self.tests_frame.grid(sticky=tk.NW,row=0,column=2,rowspan=2)
        
        self.createVariables()
        
    def createVariables(self):
        self.tcsoap_listvar = tk.StringVar()
        
        self.tcrest_listvar = tk.StringVar()
        
        self.tcdisp_var = tk.IntVar()
        
    def createWidgets(self):
        self.tcsoap_scroll = tk.Scrollbar(self.tests_frame,orient=tk.VERTICAL)
        self.tcsoap_scroll.grid(sticky=tk.N+tk.S,row=0,column=1)
        self.tcsoap_listbox = tk.Listbox(self.tests_frame,width=60,listvariable=self.tcsoap_listvar,activestyle="dotbox",yscrollcommand=self.tcsoap_scroll.set)
        self.tcsoap_listbox.grid(sticky=tk.NE,row=0,column=0)
        self.tcsoap_scroll["command"] = self.tcsoap_listbox.yview
        
        self.tcrest_scroll = tk.Scrollbar(self.tests_frame,orient=tk.VERTICAL)
        self.tcrest_scroll.grid(sticky=tk.N+tk.S,row=1,column=1)
        self.tcrest_listbox = tk.Listbox(self.tests_frame,width=60,listvariable=self.tcrest_listvar,activestyle="dotbox",yscrollcommand=self.tcrest_scroll.set)
        self.tcrest_listbox.grid(sticky=tk.NE,row=1,column=0)
        self.tcrest_scroll["command"] = self.tcrest_listbox.yview
        
        self.tcdisp_canvas = tk.Canvas(self.tests_frame,relief=tk.RIDGE,bd=2)
        
    def showTestCases(self):
        if self.DBname != "":
            self.TestCases = testcasebuilder.Transaction.getTestCaseInfo(None,self.DBname)
            
            
            self.displaymap = {}
            for key,val in self.TestCases.items(): #CReates display map of testcase description and info
                val["TCRecordId"] = key
                if val["Workflow"] == "None":                
                    self.displaymap[val["MessageType"] +"-" + re.sub(r" ","-",val["Host"]) + "-" +val["IndustryType"] + "-" + val["CardType"]] = json.dumps(val,sort_keys=True, indent=2, separators =(',',':'))
                else:
                    self.displaymap[val["MessageType"] +"-" + re.sub(r" ","-",val["Host"]) + "-" +val["IndustryType"] + "-" + val["CardType"] + "-" + val["Workflow"] + " "] = json.dumps(val,sort_keys=True, indent=2, separators =(',',':'))
            
            restkeys = []
            soapkeys = []
            for key,record in self.displaymap.items():
                if json.loads(record)["MessageType"] == "SOAP":
                    soapkeys.append(key)
                else:
                    restkeys.append(key)
            
            self.tcsoap_listvar.set("")           
            temp = ""
            for item in sorted(soapkeys):
                temp = temp + item + " "
            self.tcsoap_listvar.set(temp)
            
            self.tcrest_listvar.set("")           
            temp = ""
            for item in sorted(restkeys):
                temp = temp + item + " "
            self.tcrest_listvar.set(temp)       
                       
            self.tcsoap_listbox.bind("<ButtonRelease>",self.showInfo)
            self.tcrest_listbox.bind("<ButtonRelease>",self.showInfo)                
    
    def showInfo(self,event):        
        if event.widget.curselection() != ():            
            for Id in self.tcdisp_canvas.find_all():
                self.tcdisp_canvas.delete(Id)
            self.tcdisp_canvas.create_text(0,0,anchor=tk.NW,text=self.displaymap[event.widget.get(event.widget.curselection()[0])])
            self.tcdisp_canvas.grid(sticky=tk.NW,row=0,column=2,rowspan=2)
            if event.widget.winfo_id() == self.tcsoap_listbox.winfo_id():
                builder.soapreq_button["state"] = "active"
                builder.restreq_button["state"] = "disabled" 
                builder.soapreq_button["command"] = lambda: builder.createSOAPReq(self.DBname,json.loads(self.displaymap[event.widget.get(event.widget.curselection()[0])])["TCRecordId"][1:])
            else:
                builder.restreq_button["state"] = "active"
                builder.soapreq_button["state"] = "disabled"
                builder.restreq_button["command"] = lambda: builder.createRESTReq(self.DBname,json.loads(self.displaymap[event.widget.get(event.widget.curselection()[0])])["TCRecordId"][1:])            
                
class SaveMerchantProfileFrame:
    def __init__(self,frame,DBname):
        self.DBname = DBname        
        self.savemp_frame = tk.Frame(frame,width=275,height=250)
        self.savemp_frame.grid(sticky=tk.NW,row=0,column=1,rowspan=2)
        
        self.merchinfo = testcasebuilder.Transaction.saveMerchantProfile(None,self.DBname)
        self.merchidt = {}
        for merchname, info in self.merchinfo.items():
            self.merchidt[merchname] = info["IdentityToken"]
            del info["IdentityToken"]
        
        self.createVariables()
        
    def createVariables(self):
        self.merchselect_menubuttonvar = tk.StringVar()
        self.merchselect_menubuttonvar.set("Select Merchant Profile")
        self.merchselect_menuvar = tk.StringVar()
        
        self.merchsave_messagevar = tk.StringVar()
        
    def createWidgets(self):
        self.merchselect_menubutton = tk.Menubutton(self.savemp_frame,relief="raised",textvariable=self.merchselect_menubuttonvar)
        self.merchselect_menubutton.grid(sticky=tk.N,row=0,column=0)
        self.merchselect_menu = tk.Menu(self.merchselect_menubutton)
        self.merchselect_menubutton["menu"] = self.merchselect_menu
        self.merchselect_menubutton.bind("<Button-1>",self.populateMerchMenu)        
        
        self.merchdisp_canvas = tk.Canvas(self.savemp_frame,relief=tk.RIDGE,bd=2,width=275,height=225)
        
        self.merchsave_button = tk.Button(self.savemp_frame,text="Save Merchant Profile")
        self.merchsave_message = tk.Message(self.savemp_frame,textvariable=self.merchsave_messagevar,aspect=800)
        
    def populateMerchMenu(self,event):
        self.merchselect_menu.delete(0,tk.END)
        if builder.environment_menuitemvar.get() != "":
            for merchname, info in sorted(self.merchinfo.items()):
                if builder.environment_menuitemvar.get() == info["Environment"]:           
                    self.merchselect_menu.add_checkbutton(label=merchname,variable=self.merchselect_menuvar,onvalue=merchname,offvalue="",command=self.displayMerchRecord)
        else:
            for merchname in sorted(self.merchinfo.keys()):
                self.merchselect_menu.add_checkbutton(label=merchname,variable=self.merchselect_menuvar,onvalue=merchname,offvalue="",command=self.displayMerchRecord)
                
    def displayMerchRecord(self):
        self.merchselect_menubuttonvar.set(self.merchselect_menuvar.get())
        self.merchsave_messagevar.set("")
        
        if self.merchselect_menuvar.get() != "":                
            merchrecord = json.dumps(self.merchinfo[self.merchselect_menuvar.get()],sort_keys=True, indent=2, separators =(',',':'))
            for Id in self.merchdisp_canvas.find_all():
                self.merchdisp_canvas.delete(Id)
            self.merchdisp_canvas.create_text(0,0,anchor=tk.NW,text=merchrecord)
            self.merchdisp_canvas.grid(sticky=tk.N,row=1,column=0)
            self.merchsave_button.grid(sticky=tk.N,row=2,column=0)
            self.merchsave_button["command"] = self.saveMerchantProfile
            self.merchsave_message.grid(sticky=tk.N,row=3,column=0)
            
    def saveMerchantProfile(self):
        if self.merchselect_menuvar.get() != "":
            info = self.merchinfo[self.merchselect_menuvar.get()]
            merchdata = open("C:\\Users\\alanz\\SOATest\\pythontest\\GUIs\\data_files\\MerchantData.csv", 'w')
            merchdata.write("SaveInd,MessageType,MerchantProfileId,IndustryType,MID,TID,ServiceId,EntryMode,CustomerPresent,IdentityToken\n")
            merchdata.write("1,"+ info["MessageType"] + "," + info["MerchantProfileId"] + "," + info["IndustryType"] + "," + info["MID"] + "," +info["TID"] + "," +info["ServiceId"] + "," + info["EntryMode"] + "," + info["CustomerPresent"] + "," + self.merchidt[info["MerchantProfileId"]])
            merchdata.close()
            self.merchsave_messagevar.set("Save Merchant Profile: " + info["MerchantProfileId"] + ", added to test run.")
        
builder = TCBuildGui()
builder.master.title("TestCase Builder")
builder.mainloop()
        