import tkinter as tk

class TMSQueryGui(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self, master)
        self.grid()        
        self.main_frame = tk.Frame(self,height=400,width=400)
        self.main_frame.grid(row=0,column=0)        
        
        self.createVariables()
        self.createWidgets()
        
    def createVariables(self):
        self.tmsop_menubuttonvar = tk.StringVar()
        self.tmsop_menubuttonvar.set("Select TMS Query Type")
        self.tmsop_menuitemvar = tk.StringVar()
        
    def createWidgets(self):
        self.tmsop_menubutton = tk.Menubutton(self.main_frame,textvariable=self.tmsop_menubuttonvar,relief="raised")
        self.tmsop_menubutton.grid(row=0,column=0)
        self.tmsop_menu = tk.Menu(self.tmsop_menubutton)
        self.tmsop_menubutton["menu"] = self.tmsop_menu           
        
class TxnParamFrame:
    def __init__(self,frame,queryname):
        self.txn_frame = tk.Frame(frame,bd=4,relief=tk.RIDGE,padx=4)
        self.txn_frame.grid()
        
        self.createVariables()
        self.createLabels()
        self.createTextEntries()
        self.createListBoxes()
        self.createOtherWidgets()
        if queryname == "QueryTransactionsDetail":
            self.createDetailFormat()        
        
    def createVariables(self):
        self.amounts_var = tk.StringVar()
        self.apprvcds_var = tk.StringVar()
        self.batchids_var = tk.StringVar()
        self.merchprofids_var = tk.StringVar()
        self.ordernums_var = tk.StringVar()
        self.serviceids_var = tk.StringVar()
        self.servicekeys_var = tk.StringVar()
        self.txnids_var = tk.StringVar()
        
        self.capturestates_listvar = tk.StringVar()
        self.cardtypes_listvar = tk.StringVar()        
        self.txnstates_listvar = tk.StringVar()
        
        self.txntimestart_menubuttonvar = tk.StringVar()
        self.txntimestart_menubuttonvar.set("From Date-Time")
        self.txntimestart_menuitemvar = tk.StringVar()
        self.txntimeend_menubuttonvar = tk.StringVar()
        self.txntimeend_menubuttonvar.set("To Date-Time")
        self.txntimeend_menuitemvar = tk.StringVar()
        self.capturetimestart_menubuttonvar = tk.StringVar()
        self.capturetimestart_menubuttonvar.set("From Date-Time")
        self.capturetimestart_menuitemvar = tk.StringVar()
        self.capturetimeend_menubuttonvar = tk.StringVar()
        self.capturetimeend_menubuttonvar.set("To Date-Time")
        self.capturetimeend_menuitemvar = tk.StringVar()
        
        self.querytype_var = tk.StringVar()        
        self.includereltd_var = tk.StringVar()
        self.credsource_var = tk.StringVar()
        self.query_messagevar = tk.StringVar()
        
        self.sklist_menubuttonvar = tk.StringVar()
        self.sklist_menubuttonvar.set("Select ServiceKey")
        self.sklist_menuitemvar = tk.StringVar()
        
    def createLabels(self):
        self.txnparam_label = tk.Label(self.txn_frame,text="Query Transactions Parameters:",relief=tk.GROOVE,pady=4)
        self.txnparam_label.grid(row=0,columnspan=4)
        self.amounts_label = tk.Label(self.txn_frame,text="Amounts:")
        self.amounts_label.grid(sticky=tk.W,row=1,column=0)
        self.apprvcds_label = tk.Label(self.txn_frame,text="Approval Codes:")
        self.apprvcds_label.grid(sticky=tk.W,row=2,column=0)
        self.batchids_label = tk.Label(self.txn_frame,text="BatchIds:")
        self.batchids_label.grid(sticky=tk.W,row=3,column=0)
        self.merchprofids_label = tk.Label(self.txn_frame,text="MerchantProfileIds:")
        self.merchprofids_label.grid(sticky=tk.W,row=4,column=0)
        self.ordernums_label = tk.Label(self.txn_frame,text="Order Numbers:")
        self.ordernums_label.grid(sticky=tk.W,row=5,column=0)
        self.serviceids_label = tk.Label(self.txn_frame,text="ServiceIds:")
        self.serviceids_label.grid(sticky=tk.W,row=6,column=0)
        self.servicekeys_label = tk.Label(self.txn_frame,text="ServiceKeys:")
        self.servicekeys_label.grid(sticky=tk.W,row=7,column=0)
        self.txnids_label = tk.Label(self.txn_frame,text="Txn Guids:")
        self.txnids_label.grid(sticky=tk.W,row=8,column=0)
        
        self.capturestates_label = tk.Label(self.txn_frame,text="Capture States:")
        self.capturestates_label.grid(sticky=tk.W,row=9,column=0,rowspan=2)
        self.cardtypes_label = tk.Label(self.txn_frame,text="Card Types:")
        self.cardtypes_label.grid(sticky=tk.W,row=11,column=0,rowspan=2)        
        self.txnstates_label = tk.Label(self.txn_frame,text="Txn States:")
        self.txnstates_label.grid(sticky=tk.W,row=13,column=0,rowspan=2)
        
        self.txndatetime_label = tk.Label(self.txn_frame,text="Txn Date-Time Range:")
        self.txndatetime_label.grid(row=1,column=2,columnspan=2)
        self.capturedatetime_label = tk.Label(self.txn_frame,text="Capture Date-Time Range:")
        self.capturedatetime_label.grid(row=3,column=2,columnspan=2)
        
        self.querytype_label = tk.Label(self.txn_frame,text="Query Type:")
        self.querytype_label.grid(sticky=tk.N,row=9,column=2,columnspan=2)
        self.includereltd_label = tk.Label(self.txn_frame,text="Include Related:")
        self.includereltd_label.grid(sticky=tk.N,row=10,column=2,columnspan=2)        
    
    def createTextEntries(self):
        self.amounts_entry = tk.Entry(self.txn_frame,textvariable=self.amounts_var,width=70)
        self.amounts_entry.grid(sticky=tk.W,row=1,column=1)
        self.apprvcds_entry = tk.Entry(self.txn_frame,textvariable=self.apprvcds_var,width=70)
        self.apprvcds_entry.grid(sticky=tk.W,row=2,column=1)
        self.batchids_entry = tk.Entry(self.txn_frame,textvariable=self.batchids_var,width=70)
        self.batchids_entry.grid(sticky=tk.W,row=3,column=1)
        self.merchprofids_entry = tk.Entry(self.txn_frame,textvariable=self.merchprofids_var,width=70)
        self.merchprofids_entry.grid(sticky=tk.W,row=4,column=1)
        self.ordernums_entry = tk.Entry(self.txn_frame,textvariable=self.ordernums_var,width=70)
        self.ordernums_entry.grid(sticky=tk.W,row=5,column=1)
        self.serviceids_entry = tk.Entry(self.txn_frame,textvariable=self.serviceids_var,width=70)
        self.serviceids_entry.grid(sticky=tk.W,row=6,column=1)
        self.servicekeys_entry = tk.Entry(self.txn_frame,textvariable=self.servicekeys_var,width=70)
        self.servicekeys_entry.grid(sticky=tk.W,row=7,column=1)
        self.txnids_entry = tk.Entry(self.txn_frame,textvariable=self.txnids_var,width=70)
        self.txnids_entry.grid(sticky=tk.W,row=8,column=1)
        
    def createListBoxes(self):
        self.capturestates_listvar.set("NotSet CannotCapture ReadyForCapture CapturePending Captured CaptureDeclined InProcess CapturedUndoPermitted CapturedPendingUndoPermitted CaptureError CaptureUnknown BatchSent BatchSentUndoPermitted")
        self.capturestates_listbox = tk.Listbox(self.txn_frame,listvariable=self.capturestates_listvar,selectmode=tk.MULTIPLE,width=40,height=13,exportselection=0)
        self.capturestates_listbox.grid(sticky=tk.W,row=9,column=1,rowspan=2)
        self.cardtypes_listvar.set("Visa MasterCard Discover AmericanExpress")
        self.cardtypes_listbox = tk.Listbox(self.txn_frame,listvariable=self.cardtypes_listvar,selectmode=tk.MULTIPLE,width=40,height=4,exportselection=0)
        self.cardtypes_listbox.grid(sticky=tk.W,row=11,column=1,rowspan=2)
        self.txnstates_listvar.set("NotSet Declined Verified Authorized Adjusted Captured CaptureDeclined PartiallyCaptured Undone ReturnRequested PartialReturnRequested ReturnUndone Returned PartiallyReturned InProcess ErrorValidation ErrorUnknown")
        self.txnstates_listbox = tk.Listbox(self.txn_frame,listvariable=self.txnstates_listvar,selectmode=tk.MULTIPLE,width=40,height=17,exportselection=0)
        self.txnstates_listbox.grid(sticky=tk.W,row=13,column=1,rowspan=2)
        
    def createOtherWidgets(self):
        self.txntimestart_menubutton = tk.Menubutton(self.txn_frame,textvariable=self.txntimestart_menubuttonvar,relief="raised")
        self.txntimestart_menubutton.grid(row=2,column=2)
        self.txntimestart_menu = tk.Menu(self.txntimestart_menubutton)
        self.txntimestart_menubutton["menu"] = self.txntimestart_menu
             
        self.txntimeend_menubutton = tk.Menubutton(self.txn_frame,textvariable=self.txntimeend_menubuttonvar,relief="raised")
        self.txntimeend_menubutton.grid(row=2,column=3)
        self.txntimeend_menu = tk.Menu(self.txntimeend_menubutton)
        self.txntimeend_menubutton["menu"] = self.txntimeend_menu        
        
            
        self.capturetimestart_menubutton = tk.Menubutton(self.txn_frame,textvariable=self.capturetimestart_menubuttonvar,relief="raised")
        self.capturetimestart_menubutton.grid(row=4,column=2)
        self.capturetimestart_menu = tk.Menu(self.capturetimestart_menubutton)
        self.capturetimestart_menubutton["menu"] = self.capturetimestart_menu
        self.capturetimeend_menubutton = tk.Menubutton(self.txn_frame,textvariable=self.capturetimeend_menubuttonvar,relief="raised")
        self.capturetimeend_menubutton.grid(row=4,column=3)
        self.capturetimeend_menu = tk.Menu(self.capturetimeend_menubutton)
        self.capturetimeend_menubutton["menu"] = self.capturetimeend_menu
        
        self.querytypeor_radio = tk.Radiobutton(self.txn_frame,value="OR",variable=self.querytype_var,text="OR")
        self.querytypeor_radio.grid(row=9,column=2)        
        self.querytypeand_radio = tk.Radiobutton(self.txn_frame,value="AND",variable=self.querytype_var,text="AND")
        self.querytypeand_radio.grid(row=9,column=3)
        self.querytypeand_radio.select()
        
        self.includereltdtrue_radio = tk.Radiobutton(self.txn_frame,value="true",variable=self.includereltd_var,text="True")
        self.includereltdtrue_radio.grid(row=10,column=2)
        self.includereltdtrue_radio.select()
        self.includereltdfalse_radio = tk.Radiobutton(self.txn_frame,value="false",variable=self.includereltd_var,text="False")
        self.includereltdfalse_radio.grid(row=10,column=3)
        
        self.createquery_button = tk.Button(self.txn_frame,text="Create TMS Query")
        self.createquery_button.grid(sticky=tk.E,row=13,column=1,columnspan=2)
        
        self.credsourcetestrun_radio = tk.Radiobutton(self.txn_frame,value="testrun",variable=self.credsource_var,text="Use Authentication From Previous Test Run")
        self.credsourcetestrun_radio.grid(sticky=tk.SE,row=13,column=1,columnspan=3)
        self.credsourcetestrun_radio.select()
        self.credsourcesklist_radio = tk.Radiobutton(self.txn_frame,value="sklist",variable=self.credsource_var,text="Use Authentication From List of ServiceKeys")
        self.credsourcesklist_radio.grid(sticky=tk.NE,row=14,column=1,columnspan=3)
        
        self.sklist_menubutton = tk.Menubutton(self.txn_frame,textvariable=self.sklist_menubuttonvar,relief="raised")
        self.sklist_menu = tk.Menu(self.sklist_menubutton)
        self.sklist_menubutton["menu"] = self.sklist_menu 
        
        self.query_message = tk.Message(self.txn_frame,textvariable=self.query_messagevar,aspect=800,fg='red')
        self.query_message.grid(sticky=tk.NW,row=13,column=2,columnspan=2)          
                
    def createDetailFormat(self):
        self.txndetlfrmt_var = tk.StringVar()
        
        self.txndetlfrmt_label = tk.Label(self.txn_frame,text="Transaction Format:")
        self.txndetlfrmt_label.grid(sticky=tk.N,row=11,column=2,columnspan=2)
        
        self.txndetlfrmttxn_radio = tk.Radiobutton(self.txn_frame,value="CWSTransaction",variable=self.txndetlfrmt_var,text="CWS Transaction")
        self.txndetlfrmttxn_radio.grid(sticky=tk.N,row=12,column=2)
        self.txndetlfrmttxn_radio.select()
        self.txndetlfrmtsrl_radio = tk.Radiobutton(self.txn_frame,value="SerializedCWS",variable=self.txndetlfrmt_var,text="Serialized CWS")
        self.txndetlfrmtsrl_radio.grid(sticky=tk.N,row=12,column=3)
        
class BatchParamFrame:
    def __init__(self,frame):
        self.batch_frame = tk.Frame(frame)
        
