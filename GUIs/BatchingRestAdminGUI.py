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
        self.batchselector_menubuttonvar = tk.StringVar()
        self.batchselector_menubuttonvar.set("Choose Selector")
        self.batchselector_menuitemvar = tk.StringVar()
        
        self.batchvalue_var = tk.StringVar()
        
    def createWidgets(self):
        self.batchselector_menubutton = tk.Menubutton(self.main_frame,textvariable=self.batchselector_menubuttonvar,relief="raised")
        self.batchselector_menubutton.grid(sticky=tk.NW,row=0,column=0)
        self.batchselector_menu = tk.Menu(self.batchselector_menubutton)
        self.batchselector_menubutton["menu"] = self.batchselector_menu
        for selector in ["ptlsSessionToken","serviceKey","profileName"]:
            self.batchselector_menu.add_checkbutton(label=selector,variable=self.batchselector_menuitemvar,onvalue=selector,offvalue="",command=self.updateSelectorMenu)
            
        self.batchvalue_entry = tk.Entry(self.main_frame,textvariable=self.batchvalue_var,width=40)
        self.batchvalue_entry.grid(sticky=tk.NW,row=0,column=1)
        
        self.batchsend_button = tk.Button(self.main_frame,text="Send Request",state="disabled",command=self.sendbatchRequest)
        self.batchsend_button.grid(sticky=tk.NW,row=0,column=2)
        
        self.batchresult_canvas = tk.Canvas(self.main_frame,relief=tk.RIDGE,bd=2)
            
    def updateSelectorMenu(self):
        self.batchselector_menubuttonvar.set(self.batchselector_menuitemvar.get())
        if self.batchselector_menuitemvar.get() != "":
            self.batchsend_button["state"] = "active"
        else:
            self.batchsend_button["state"] = "disabled"
            
    def sendbatchRequest(self):
        url = "http://10.173.135.18/batch/resend?" + self.batchselector_menubuttonvar.get() + "='" + self.batchvalue_var.get() + "'"
        r = requests.get(url)
        self.batchresult_canvas.create_text(5,5,anchor=tk.NW,text="HTTP Status Code = " + str(r.status_code) + "\n" + r.text)
        self.batchresult_canvas.grid(sticky=tk.N,row=1,column=0,columnspan=3)
        
        
restgui = RESTAdmin()
restgui.master.title("CWS REST Admin")
restgui.mainloop()