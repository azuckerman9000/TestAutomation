import requests
import re
import tkinter as tk


class RESTAdmin(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.main_frame = tk.Frame(self)
        self.main_frame.grid()        
        
        self.createVariables()
        self.createWidgets()
        
    def createVariables(self):        
        self.sessiontoken_var = tk.StringVar()
        self.servicekey_var = tk.StringVar()
        self.profilename_var = tk.StringVar()
        
        self.send_messagevar = tk.StringVar()
        self.baseip_var = tk.StringVar()
        self.baseip_var.set("10.173.135.15")
        
    def createWidgets(self):        
        self.sessiontoken_label = tk.Label(self.main_frame,text="PTLSSessionToken: ")
        self.sessiontoken_label.grid(sticky=tk.NW,row=0,column=0)
        self.servicekey_label = tk.Label(self.main_frame,text="ServiceKey: ")
        self.servicekey_label.grid(sticky=tk.NW,row=1,column=0)
        self.profilename_label = tk.Label(self.main_frame,text="MerchantProfileId: ")
        self.profilename_label.grid(sticky=tk.NW,row=2,column=0)
        self.baseip_label = tk.Label(self.main_frame,text="Host: ")
        self.baseip_label.grid(sticky=tk.NW,row=3,column=0)
        
        self.sessiontoken_entry = tk.Entry(self.main_frame,textvariable=self.sessiontoken_var,width=70)
        self.sessiontoken_entry.grid(sticky=tk.NW,row=0,column=1)
        self.servicekey_entry = tk.Entry(self.main_frame,textvariable=self.servicekey_var,width=70)
        self.servicekey_entry.grid(sticky=tk.NW,row=1,column=1)
        self.profilename_entry = tk.Entry(self.main_frame,textvariable=self.profilename_var,width=70)
        self.profilename_entry.grid(sticky=tk.NW,row=2,column=1)
        self.baseip_entry = tk.Entry(self.main_frame,textvariable=self.baseip_var,width=70)
        self.baseip_entry.grid(sticky=tk.NW,row=3,column=1)
        
        self.send_button = tk.Button(self.main_frame,text="Send Request",command=self.sendRequest)
        self.send_button.grid(row=4,column=0,columnspan=2)
        
        self.send_message = tk.Message(self.main_frame,textvariable=self.send_messagevar,aspect=1000)
        self.send_message.grid(row=5,column=0,columnspan=2)
        
        self.result_canvas = tk.Canvas(self.main_frame,relief=tk.RIDGE,bd=2,width=600) 
            
    def sendRequest(self):
        for Id in self.result_canvas.find_all():
            self.result_canvas.delete(Id)
        
        if self.sessiontoken_var.get() == "" or self.servicekey_var.get() == "":
            self.send_messagevar.set("PTLSSessionToken and ServiceKey are required!")
            self.send_message["fg"] = "red"
            return
        url = "http://" + self.baseip_var.get() + "/Admin/batch/resend?ptlsSessionToken=" + self.sessiontoken_var.get() + "&serviceKey=" + self.servicekey_var.get()
        if self.profilename_entry.get() != "":
            url += "&profileName=" + self.profilename_entry.get()
        
        try:
            r = requests.post(url)
            successcode = re.search('(?:<IsSuccess>)(\w+)',r.text)
            respmessage = re.search('(?:<Message>)([\w ]+)',r.text)
            self.send_messagevar.set("ReSend Batch Request Sent.")
            self.send_message["fg"] = "blue"                             
            self.result_canvas.create_text(5,5,anchor=tk.NW,text="HTTP Status Code = " + str(r.status_code) + "\nIsSuccess = " + successcode.group(1) + "\nMessage = " +respmessage.group(1))            
        except requests.exceptions.RequestException as errorstr:            
            self.result_canvas.create_text(5,5,anchor=tk.NW,text=errorstr,width=600)
            self.send_messagevar.set("An Exception Occurred.")
            self.send_message["fg"] = "red" 
        self.result_canvas.grid(sticky=tk.N,row=6,column=0,columnspan=2)
        
restgui = RESTAdmin()
restgui.master.title("TPS:Re-Send Batch")
restgui.mainloop()