import TMSGui
from automation import tmsquerybuilder as QB
import tkinter as tk

class TMSGuiController:
    def __init__(self):
        self.gui = TMSGui.TMSQueryGui()
        self.gui.master.title("TMS Queries")
        #self.gui.mainloop()
        for item in ["QueryTransactionsSummary","QueryTransactionsFamily","QueryTransactionsDetail","QueryBatch"]:
            self.gui.tmsop_menu.add_checkbutton(label=item,onvalue=item,variable=self.gui.tmsop_menuitemvar,command=self.openParamFrame)
        
    def openParamFrame(self):        
        self.gui.tmsop_menubuttonvar.set(self.gui.tmsop_menuitemvar.get())
        if "param_frame" in self.gui.__dict__.keys():
            self.gui.param_frame.txn_frame.grid_forget()
            self.gui.param_frame.txn_frame.destroy()
            del self.gui.param_frame
        if self.gui.tmsop_menuitemvar.get() != "QueryBatch" and self.gui.tmsop_menuitemvar.get() != "":            
            self.gui.param_frame = TMSGui.TxnParamFrame(self.gui.main_frame,self.gui.tmsop_menuitemvar.get())
            self.setUpTxnParamCallBacks()            
        elif self.gui.tmsop_menuitemvar.get() == "QueryBatch":
            self.gui.param_frame = TMSGui.BatchParamFrame(self.gui.main_frame)
            self.setUpBatchParamCallBacks()
        
    def setUpTxnParamCallBacks(self):
        self.times = ["Now","One Hour Ago","Four Hours Ago","Eight Hours Ago","One Day Ago","Two Days Ago","One Week Ago","One Month Ago"]
        for item in self.times[1:8]:
            self.gui.param_frame.txntimestart_menu.add_checkbutton(label=item,onvalue=item,variable=self.gui.param_frame.txntimestart_menuitemvar,offvalue="",command=lambda: self.timeStartMenuLogic("txn"))
        for item in self.times[1:8]:
            self.gui.param_frame.capturetimestart_menu.add_checkbutton(label=item,onvalue=item,variable=self.gui.param_frame.capturetimestart_menuitemvar,offvalue="",command=lambda: self.timeStartMenuLogic("capture"))
            
        self.gui.param_frame.createquery_button["command"] = self.getInputValues
        self.gui.param_frame.credsourcesklist_radio["command"] = self.chooseCreds
        self.gui.param_frame.credsourcetestrun_radio["command"] = self.chooseCreds        
    
    def setUpBatchParamCallBacks(self):
        self.times = ["Now","One Hour Ago","Four Hours Ago","Eight Hours Ago","One Day Ago","Two Days Ago","One Week Ago","One Month Ago"]
        for item in self.times[1:8]:
            self.gui.param_frame.batchtimestart_menu.add_checkbutton(label=item,onvalue=item,variable=self.gui.param_frame.batchtimestart_menuitemvar,offvalue="",command=lambda: self.timeStartMenuLogic("batch"))
        
        self.gui.param_frame.createquery_button["command"] = self.getInputValues
        self.gui.param_frame.credsourcesklist_radio["command"] = self.chooseCreds
        self.gui.param_frame.credsourcetestrun_radio["command"] = self.chooseCreds
        
    def timeStartMenuLogic(self,varkey):
        self.gui.param_frame.__dict__[varkey + "timeend_menu"].delete(0,tk.END)             #Deletes any existing menu options in the "To" menu if they exist - due to re-selecting From time
        starttime = self.gui.param_frame.__dict__[varkey + "timestart_menuitemvar"].get()   #Gets the selected time value of the From menu
        self.gui.param_frame.__dict__[varkey+ "timestart_menubuttonvar"].set(starttime)     #Updates From menubutton with selected value
        if self.gui.param_frame.__dict__[varkey + "timeend_menubuttonvar"].get() not in ["To Date-Time", ""]: #If previously an option was selected in the To menu, reverts button text to default and deletes the menu variable
            self.gui.param_frame.__dict__[varkey + "timeend_menubuttonvar"].set("To Date-Time")
            self.gui.param_frame.__dict__[varkey + "timeend_menuitemvar"].set("") 
        for item in self.times[0:self.times.index(starttime)]:                              #Populates the To menu with conditional values based on the From menu selection value
            self.gui.param_frame.__dict__[varkey + "timeend_menu"].add_checkbutton(label=item,onvalue=item,variable=self.gui.param_frame.__dict__[varkey + "timeend_menuitemvar"],offvalue="",command=lambda: self.updateTimeEndMenu(varkey))
    
    def chooseCreds(self):
        if self.gui.param_frame.credsource_var.get() == "sklist":            
            self.gui.param_frame.sklist_menubutton.grid(sticky=tk.W,row=14,column=2,columnspan=2)
            self.sklist = QB.getCredentials()
            for item in self.sklist.keys():
                self.gui.param_frame.sklist_menu.add_checkbutton(label=item,onvalue=item,variable=self.gui.param_frame.sklist_menuitemvar,offvalue="",command=self.updateSklistMenu)
        elif self.gui.param_frame.credsource_var.get() == "testrun":
            self.gui.param_frame.sklist_menu.delete(0,tk.END)
            self.gui.param_frame.sklist_menubuttonvar.set("Select ServiceKey")
            self.gui.param_frame.sklist_menuitemvar.set("")
            self.gui.param_frame.sklist_menubutton.grid_forget()
                
    def updateSklistMenu(self):
        self.gui.param_frame.sklist_menubuttonvar.set(self.gui.param_frame.sklist_menuitemvar.get())
    
    def updateTimeEndMenu(self,varkey):
        self.gui.param_frame.__dict__[varkey + "timeend_menubuttonvar"].set(self.gui.param_frame.__dict__[varkey + "timeend_menuitemvar"].get())
        
    def getInputValues(self):
        self.queryparams = {}
        for key,val in self.gui.param_frame.__dict__.items(): 
            if key.find("var") != -1 and val.get() != "":   #Narrows down items to populate self.queryparams with - widget variables that are not empty strings             
                if key.find("list") == -1 and key.find("button") == -1 and key.find("message") == -1 and key.find("credsource") == -1 and key.find("sklist") == -1: #Narrows down items to populate self.queryparams with - widget variables that are not listvars or buttonvars or messagevars or the credsourcevar
                    self.queryparams[key] = val.get().split(",")
        
        for varkey in ["batch","txn","capture"]:
            varintersection = set([varkey + "timestart_menuitemvar",varkey + "timeend_menuitemvar"]) & set(list(self.queryparams.keys()))
            if varintersection != set([]):
                if varintersection != set([varkey + "timestart_menuitemvar",varkey + "timeend_menuitemvar"]):
                    self.gui.param_frame.query_messagevar.set("Missing " + varkey + " daterange value")
                    return
                else:
                    self.gui.param_frame.query_messagevar.set("")                    
        
        if self.gui.tmsop_menuitemvar.get() != "QueryBatch":                        
            for listbox in ["capturestates","cardtypes","txnstates"]:           #block for finding any selections in the listboxes
                if self.gui.param_frame.__dict__[listbox + "_listbox"].curselection() != (): #Checks if there is any selection in the current listbox by comparing selection vs empty tuple
                    self.queryparams[listbox] = []                                           #Prepares a dict entry as a list for selected entries
                    for index in self.gui.param_frame.__dict__[listbox + "_listbox"].curselection(): #For each selection, append it to list in dict created above
                        self.queryparams[listbox].append(self.gui.param_frame.__dict__[listbox + "_listbox"].get(index))
        
        self.Query = QB.QueryBuilder(self.queryparams)
        if self.gui.param_frame.credsource_var.get() == "sklist":
            QB.buildDataSource(self.Query.dataload,self.Query.colnames,self.gui.tmsop_menuitemvar.get(),self.sklist[self.gui.param_frame.sklist_menuitemvar.get()])
        elif self.gui.param_frame.credsource_var.get() == "testrun":
            QB.buildDataSource(self.Query.dataload,self.Query.colnames,self.gui.tmsop_menuitemvar.get(),None)
        self.gui.param_frame.query_messagevar.set("Query Built.")
                
            
app = TMSGuiController()
app.gui.mainloop()

