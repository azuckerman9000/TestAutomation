import requests
from requests.auth import HTTPBasicAuth
import tkinter as tk

#Online Batching Queues:
#BMS.BatchSummary
#BMS.BatchTxnFragment
#TbWcf.GenericRequestQueue
#TbWcf.GenericResponseQueue
#TPS.Batch.Request
#TPS.Batch.Response

class RESTAdmin(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.main_frame = tk.Frame(self,height=400,width=500)
        self.main_frame.grid()
        self.main_frame.grid_propagate(0)
        
        self.createVariables()
        self.createWidgets()
        
    def createVariables(self):
        self.TSUselector_menubuttonvar = tk.StringVar()
        self.TSUselector_menubuttonvar.set("Choose Selector")
        self.TSUselector_menuitemvar = tk.StringVar()
        
        self.TSUvalue_var = tk.StringVar()
        
    def createWidgets(self):
        self.TSUselector_menubutton = tk.Menubutton(self.main_frame,textvariable=self.TSUselector_menubuttonvar,relief="raised")
        self.TSUselector_menubutton.grid(sticky=tk.NW,row=0,column=0)
        self.TSUselector_menu = tk.Menu(self.TSUselector_menubutton)
        self.TSUselector_menubutton["menu"] = self.TSUselector_menu
        for selector in ["PTLS_IppfServiceId","PTLS_ServiceKey","PTLS_MerchId"]:
            self.TSUselector_menu.add_checkbutton(label=selector,variable=self.TSUselector_menuitemvar,onvalue=selector,offvalue="",command=self.updateSelectorMenu)
            
        self.TSUvalue_entry = tk.Entry(self.main_frame,textvariable=self.TSUvalue_var,width=40)
        self.TSUvalue_entry.grid(sticky=tk.NW,row=0,column=1)
        
        self.TSUsend_button = tk.Button(self.main_frame,text="Send Request",state="disabled",command=self.sendTSURequest)
        self.TSUsend_button.grid(sticky=tk.NW,row=0,column=2)
        
        self.TSUresult_canvas = tk.Canvas(self.main_frame,relief=tk.RIDGE,bd=2)
            
    def updateSelectorMenu(self):
        self.TSUselector_menubuttonvar.set(self.TSUselector_menuitemvar.get())
        if self.TSUselector_menuitemvar.get() != "":
            self.TSUsend_button["state"] = "active"
        else:
            self.TSUsend_button["state"] = "disabled"
            
    def sendTSURequest(self):
        url = "http://10.173.135.23/TPS/TxnStatusUpdate/ResendTransactionStatusUpdate?selector=" + self.TSUselector_menubuttonvar.get() + "='" + self.TSUvalue_var.get() + "'"
        r = requests.get(url)
        self.TSUresult_canvas.create_text(5,5,anchor=tk.NW,text="HTTP Status Code = " + str(r.status_code) + "\n" + r.text)
        self.TSUresult_canvas.grid(sticky=tk.N,row=1,column=0,columnspan=3)
        
        
restgui = RESTAdmin()
restgui.master.title("CWS REST Admin")
restgui.mainloop()