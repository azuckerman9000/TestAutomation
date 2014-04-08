from automation import datacreate
import tkinter as tk
import json
from globalvars import globalvars

class GuiFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.main_frame = tk.Frame(self,height=200, width=400, bd=3)           
        self.main_frame.grid(sticky=tk.NW,row=0,column=0)
        self.main_frame.grid_propagate(0)        
        
        self.getWidgetFrames()
        self.createWidgets()
        
        self.DB_Init_button = tk.Button(self.main_frame, text='Initialize DB',command=self.DBInitbuttonLogic)
        self.DB_Init_button.grid(sticky=tk.NW,row=0,column=0) 
    
    def getWidgetFrames(self):
        self.prop_frame = NewPropertyFrame(self)            
        self.prop_frame.createPropWidgets()
        
        self.rec_frame = UpdateRecordFrame(self)
        self.viewrec_frame = ViewRecordsFrame(self)
    
    def createWidgets(self):
        self.createclasses_button = tk.Button(self.main_frame,text='Create New Classes', state='disabled')
        self.createclasses_button.grid(sticky=tk.NW,row=1,column=0)
        
        self.createprops_button = tk.Button(self.main_frame, text='Create New Class Properties',state='disabled')
        self.createprops_button.grid(sticky=tk.NW,row=2,column=0)
        
        self.createrecords_button = tk.Button(self.main_frame, text='Create New Records',state='disabled')
        self.createrecords_button.grid(sticky=tk.NW,row=3,column=0)
        
        self.createlinks_button = tk.Button(self.main_frame, text='Link Records',state='disabled')
        self.createlinks_button.grid(sticky=tk.NW,row=4,column=0)
        
        self.dumprecords_button = tk.Button(self.main_frame, text='Dump Records to File',state='disabled')
        self.dumprecords_button.grid(sticky=tk.NW,row=0,column=1)
        
        self.dumpproperties_button = tk.Button(self.main_frame, text='Dump Properties to File',state='disabled')
        self.dumpproperties_button.grid(sticky=tk.NW,row=1,column=1)
        
    def DBInitbuttonLogic(self):        
        self.DB = datacreate.Database()
        self.DB_Init_button["state"] = "disabled"
        
        self.createclasses_button["state"] = "active"
        self.createclasses_button["command"] = self.DB.createClass
        
        self.createprops_button["state"] = "active"
        self.createprops_button["command"] = self.DB.createClassProperties
        
        self.createrecords_button["state"] = "active"
        self.createrecords_button["command"] = self.addRecords
        
        self.createlinks_button["state"] = "active"
        self.createlinks_button["command"] = self.DB.updateRecordLinks
        
        self.dumprecords_button["state"] = "active"
        self.dumprecords_button["command"] = self.DB.dumpRecords
        
        self.dumpproperties_button["state"] = "active"
        self.dumpproperties_button["command"] = self.DB.dumpProperties
        
        self.prop_frame.setWidgetsActive()
        self.prop_frame.addPropClassMenuItems()
        self.prop_frame.addPropTypeMenuItems()
        
        self.viewrec_frame.populateMenus()
        
    def addRecords(self):
        self.DB.addRecords()
        if self.DB.startlinkframe == True:
            self.mapping_frame = CreateMapRowFrame(self.DB)
            self.mapping_frame.mainloop()             
            
class CreateMapRowFrame(tk.Frame):
    def __init__(self,DB,master=None):
        tk.Frame.__init__(self, master=None)
        self.grid()
        self.createmaps_frame = tk.Toplevel(height=400,width=400)
        self.createmaps_frame.grid()
        
        self.DB = DB
        
        self.reckey_classname = {}
        self.reckey_recordid = {}               
        for classname, reclist in self.DB.recstolink.items():
            for recinfo in reclist:
                self.reckey_classname[recinfo[1]] = classname
                self.reckey_recordid[recinfo[1]] = recinfo[0]
        
        self.linkkey_classname = {}
        self.linkkey_recordid = {}
        self.classname_linkkeys = {}    
        for classname, choicelist in self.DB.linkchoices.items():
            self.classname_linkkeys[classname] = []
            for choiceinfo in choicelist:
                self.linkkey_classname[choiceinfo[1]] = classname
                self.linkkey_recordid[choiceinfo[1]] = choiceinfo[0]
                self.classname_linkkeys[classname].append(choiceinfo[1])        
            
        self.createVariables()
        self.createWidgets()        
        
    def createVariables(self):
        self.recordstolink_listvar = tk.StringVar()
        for reckey in self.reckey_classname.keys():
            self.recordstolink_listvar.set(self.recordstolink_listvar.get() + reckey + " ")                       
        
        self.linkchoices_listvar = tk.StringVar()        
    
    def createWidgets(self):
        self.recordstolink_scroll = tk.Scrollbar(self.createmaps_frame,orient=tk.VERTICAL)
        self.recordstolink_scroll.grid(sticky=tk.N+tk.S,row=0,column=1)        
        self.recordstolink_listbox = tk.Listbox(self.createmaps_frame,width=30,listvariable=self.recordstolink_listvar,activestyle="dotbox",yscrollcommand=self.recordstolink_scroll.set,exportselection=0)
        self.recordstolink_scroll["command"] = self.recordstolink_listbox.yview
        self.recordstolink_listbox.grid(sticky=tk.N,row=0,column=0)
        
        self.recordstolink_display = tk.Canvas(self.createmaps_frame,relief=tk.RIDGE,bd=2)
        
        self.linkchoices_scroll = tk.Scrollbar(self.createmaps_frame,orient=tk.VERTICAL)
        self.linkchoices_scroll.grid(sticky=tk.N+tk.S,row=0,column=3)        
        self.linkchoices_listbox = tk.Listbox(self.createmaps_frame,width=30,listvariable=self.linkchoices_listvar,activestyle="dotbox",yscrollcommand=self.linkchoices_scroll.set,exportselection=0)
        self.linkchoices_scroll["command"] = self.linkchoices_listbox.yview
        self.linkchoices_listbox.grid(sticky=tk.N,row=0,column=2)
        
        self.linkchoicesdisplay_scroll = tk.Scrollbar(self.createmaps_frame,orient=tk.VERTICAL)
        self.linkchoices_display = tk.Canvas(self.createmaps_frame,relief=tk.RIDGE,bd=2,yscrollcommand=self.linkchoicesdisplay_scroll.set)
        self.linkchoicesdisplay_scroll["command"] = self.linkchoices_display.yview
        
        self.createmaprow_button = tk.Button(self.createmaps_frame,text="Create Map Row",state="disabled",command=self.createMapFileRow)
        self.createmaprow_button.grid(sticky=tk.N,row=2,column=1,columnspan=2)
        
        self.recordstolink_listbox.bind("<ButtonRelease>",self.showRecordsToLink)
        
    def showRecordsToLink(self,event):
        selectedrec = event.widget.get(event.widget.curselection()[0])
        if self.reckey_classname[selectedrec] in ["Service","Credentials"]:
            self.linkchoices_listbox["selectmode"] = tk.MULTIPLE
        else:
            self.linkchoices_listbox["selectmode"] = tk.BROWSE
        for Id in self.recordstolink_display.find_all():
            self.recordstolink_display.delete(Id)
        self.recordstolink_display.create_text(0,0,anchor=tk.NW,text=self.DB.getRecord(self.reckey_recordid[selectedrec],0))
        self.recordstolink_display.grid(sticky=tk.N,row=1,column=0,columnspan=2)
        self.createmaprow_button["state"] = "disabled"
        self.showPossibleLinks(self.reckey_classname[selectedrec])
        
    def showPossibleLinks(self,classname):
        for Id in self.linkchoices_display.find_all():
            self.linkchoices_display.delete(Id)
        for selection in self.linkchoices_listbox.curselection():
            self.linkchoices_listbox.delete(selection)
        templistvar = ""
        for linkkey in self.classname_linkkeys[classname]:
            templistvar += linkkey + " "            
        self.linkchoices_listvar.set(templistvar)             
        self.linkchoices_listbox.bind("<ButtonRelease>",self.selectChoices)
        
    def selectChoices(self,event):
        for Id in self.linkchoices_display.find_all():
            self.linkchoices_display.delete(Id)   
        self.choices = []        
        if len(event.widget.curselection()) >= 1:            
            for index in event.widget.curselection():
                self.choices.append(event.widget.get(index))        
        text = ""
        if len(self.choices) >= 1:
            for choice in self.choices:
                text = text + self.DB.getRecord(self.linkkey_recordid[choice],0) + "\n"
            self.linkchoices_display.create_text(0,0,anchor=tk.NW,text=text)
            self.linkchoices_display.config(scrollregion=self.linkchoices_display.bbox(tk.ALL))
            self.linkchoices_display.grid(sticky=tk.N,row=1,column=2,columnspan=2)
            self.linkchoicesdisplay_scroll.grid(sticky=tk.NW+tk.SW,row=1,column=4,columnspan=2)
            self.createmaprow_button["state"] = "active"
        else:
            self.createmaprow_button["state"] = "disabled"
            
    def createMapFileRow(self):
        if len(self.choices) >= 1:
            rowtemplate = {}
            selectedrec = self.recordstolink_listbox.get(self.recordstolink_listbox.curselection()[0])
            rowtemplate["Id"] = selectedrec
            rowtemplate["@class"] = self.reckey_classname[selectedrec]
            if self.reckey_classname[selectedrec] == "Service":
                rowtemplate["Key"] = "Svc"                
                rowtemplate["MapList"] = list(self.choices)
            elif self.reckey_classname[selectedrec] == "Credentials":
                rowtemplate["Key"] = "SK"                
                rowtemplate["MapList"] = list(self.choices)
            elif self.reckey_classname[selectedrec] == "Merchant":
                rowtemplate["Key"] = "Merch"                
                rowtemplate["MapList"] = self.choices[0]
            elif self.reckey_classname[selectedrec] == "Application":
                rowtemplate["Key"] = "App"                
                rowtemplate["MapList"] = self.choices[0]
            print(rowtemplate)
            del self.reckey_classname[selectedrec]
            if len(self.reckey_classname.keys()) != 0:                
                templistvar = ""
                for reckey in self.reckey_classname.keys():
                    templistvar += reckey + " "
                self.recordstolink_listvar.set(templistvar)
            else:
                self.createmaps_frame.destroy()
                self.quit()
                
class NewPropertyFrame:
    def __init__(self,frame):        
        self.newprop_frame = tk.Frame(frame,height=200, width=400)           
        self.newprop_frame.grid(sticky=tk.NW,row=1,column=0)
        self.newprop_frame.grid_propagate(0)
        self.createMenuVariables()                
    
    def createMenuVariables(self):
        self.prop_class_menuvar = tk.StringVar()
        self.prop_class_menuvar.set("Select Class")
        self.prop_class_menuitemvar = tk.StringVar()
        
        self.prop_type_menuvar = tk.StringVar()
        self.prop_type_menuvar.set("Select Property Type")
        self.prop_type_menuitemvar = tk.StringVar()
        
        self.prop_name_var = tk.StringVar()
        
        self.linkclass_menuvar = tk.StringVar()
        self.linkclass_menuvar.set("Select Class to Link")
        self.linkclass_menuitemvar = tk.StringVar()        
        
    def createPropWidgets(self):
        self.prop_class_label = tk.Label(self.newprop_frame, text = "Property for Class:")
        self.prop_class_label.grid(sticky=tk.NW,row=0,column=0)        
        self.prop_class_menubutton = tk.Menubutton(self.newprop_frame, relief="raised",textvariable=self.prop_class_menuvar, state="disabled")
        self.prop_class_menubutton.grid(sticky=tk.NW,row=0,column=1)        
        self.prop_class_menu = tk.Menu(self.prop_class_menubutton)
        self.prop_class_menubutton["menu"] = self.prop_class_menu        
        
        self.prop_name_label = tk.Label(self.newprop_frame, text = "Enter New Property Name:")
        self.prop_name_label.grid(sticky=tk.NW,row=1,column=0)        
        self.prop_name_entry =tk.Entry(self.newprop_frame,textvariable=self.prop_name_var,state="disabled")
        self.prop_name_entry.grid(sticky=tk.NW,row=1,column=1)
        
        self.prop_type_label = tk.Label(self.newprop_frame, text = "Property Type:")
        self.prop_type_label.grid(sticky=tk.NW,row=2,column=0)
        self.prop_type_menubutton = tk.Menubutton(self.newprop_frame, relief="raised",textvariable=self.prop_type_menuvar, state="disabled")
        self.prop_type_menubutton.grid(sticky=tk.NW,row=2,column=1)
        self.prop_type_menu = tk.Menu(self.prop_type_menubutton)
        self.prop_type_menubutton["menu"] = self.prop_type_menu
        
        self.linkclass_label = tk.Label(self.newprop_frame, text = "Link to Class:")
        self.linkclass_menubutton = tk.Menubutton(self.newprop_frame, relief="raised",textvariable=self.linkclass_menuvar)
        self.linkclass_menu = tk.Menu(self.linkclass_menubutton)
        self.linkclass_menubutton["menu"] = self.linkclass_menu
        
        self.addprop_button = tk.Button(self.newprop_frame, text="Add New Property",state="disabled",command=self.addNewProperty)
        self.addprop_button.grid(sticky=tk.NW,row=3,column=0)
        
    def addPropClassMenuItems(self):
        for item in gui.DB.ClassNames:
            self.prop_class_menu.add_checkbutton(label=item,variable=self.prop_class_menuitemvar,onvalue=item, command=self.updateClassButton)
    
    def updateClassButton(self):
        self.prop_class_menuvar.set(self.prop_class_menuitemvar.get())
        if self.prop_type_menuvar.get().find("LINK") != -1:
            self.linkclass_menu.delete(0,self.linkclass_menu.index(tk.END))
            self.linkclass_menuvar.set("Select Class to Link")
            self.linkclass_menuitemvar.set("")
            self.addLinkClassMenuItems()
            
    def addPropTypeMenuItems(self):        
        for item in globalvars.PROPERTYTYPES:
            self.prop_type_menu.add_checkbutton(label=item,variable=self.prop_type_menuitemvar,onvalue=item, command=self.updateProptypeButton)
            
    def updateProptypeButton(self):
        self.prop_type_menuvar.set(self.prop_type_menuitemvar.get())
        if self.prop_type_menuvar.get().find("LINK") != -1:
            self.linkclass_label.grid(sticky=tk.NW,row=3,column=0)
            self.linkclass_menubutton.grid(sticky=tk.NW,row=3,column=1)
            self.addprop_button.grid(sticky=tk.NW,row=4,column=0)
            self.addLinkClassMenuItems()
        else:
            self.addprop_button.grid(sticky=tk.NW,row=3,column=0)
            self.linkclass_label.grid_forget()
            self.linkclass_menubutton.grid_forget()
    
    def addLinkClassMenuItems(self):
        for item in gui.DB.ClassNames:
            if item != self.prop_class_menuvar.get():
                self.linkclass_menu.add_checkbutton(label=item,variable=self.linkclass_menuitemvar,onvalue=item,command=self.updateLinkClassButton)
                
    def updateLinkClassButton(self):
        self.linkclass_menuvar.set(self.linkclass_menuitemvar.get())
        
    def addNewProperty(self):
        if self.linkclass_menuvar.get().find("LINK") != -1:
            if self.prop_class_menuitemvar.get() != "" and self.prop_name_var.get() != "" and self.prop_type_menuitemvar.get() != "" and self.linkclass_menuitemvar.get() != "":
                args = self.prop_name_var.get() + "=" + self.prop_type_menuitemvar.get() + "=" + self.linkclass_menuitemvar.get()
                gui.DB.addProperty(self.prop_class_menuitemvar,*args)
            else:
                print("Invalid Entries")
        else:
            if self.prop_class_menuitemvar.get() != "" and self.prop_name_var.get() != "" and self.prop_type_menuitemvar.get() != "":
                args = self.prop_name_var.get() + "=" + self.prop_type_menuitemvar.get()
                gui.DB.addProperty(self.prop_class_menuitemvar.get(),args)
            else:
                print("Invalid Entries")
        
    def setWidgetsActive(self):
        self.prop_class_menubutton["state"] = "active"
        self.prop_name_entry["state"] = "normal"
        self.prop_type_menubutton["state"] = "active"
        self.addprop_button["state"] = "active"

class UpdateRecordFrame:
    def __init__(self,frame):
        self.updaterec_frame = tk.Frame(frame,height=200, width=500)
        self.updaterec_frame.grid(row=2,column=0)
        self.updaterec_frame.grid_propagate(0)
        
        self.record_var = tk.StringVar()        
        self.record_label = tk.Label(self.updaterec_frame,text="Enter RecordId:")
        self.record_label.grid(sticky=tk.NW,row=0,column=0)
        self.record_entry = tk.Entry(self.updaterec_frame,textvariable=self.record_var,state="normal")
        self.record_entry.grid(sticky=tk.NW,row=0,column=1)
        
        self.updaterec_var = tk.StringVar()
        self.updaterec_var.set("Update Record")
        self.updaterec_button = tk.Button(self.updaterec_frame,textvariable=self.updaterec_var, command=self.updateRecord)
        
        self.fieldinfo = {}
        self.fieldwidgets = {}        
        self.createWidgets()    
               
        
    def createWidgets(self):
        self.row = 1
        if self.fieldwidgets.keys() != []:
            self.row = int(len(self.fieldinfo.keys())/3 + 1)
                
        self.fieldinfo["fieldkey_var" + str(self.row)] = tk.StringVar()
        self.fieldinfo["fieldval_var" + str(self.row)] = tk.StringVar()  
        self.fieldinfo["fieldadd_var" + str(self.row)] = tk.StringVar() 
        self.fieldinfo["fieldadd_var" + str(self.row)].set("Add")                        
        
        self.fieldwidgets["fieldkey_label" + str(self.row)] = tk.Label(self.updaterec_frame,text="Enter Field Name:")
        self.fieldwidgets["fieldkey_label" + str(self.row)].grid(sticky=tk.NW,row=self.row,column=0)        
        self.fieldwidgets["fieldkey_entry" + str(self.row)] = tk.Entry(self.updaterec_frame,textvariable=self.fieldinfo["fieldkey_var" + str(self.row)],state="normal")
        self.fieldwidgets["fieldkey_entry" + str(self.row)].grid(sticky=tk.NW,row=self.row,column=1)
        
        self.fieldwidgets["fieldval_label" + str(self.row)] = tk.Label(self.updaterec_frame,text="Enter Field Value:")
        self.fieldwidgets["fieldval_label" + str(self.row)].grid(sticky=tk.NW,row=self.row,column=2)
        self.fieldwidgets["fieldval_entry" + str(self.row)] = tk.Entry(self.updaterec_frame,textvariable=self.fieldinfo["fieldval_var" + str(self.row)],state="normal")
        self.fieldwidgets["fieldval_entry" + str(self.row)].grid(sticky=tk.NW,row=self.row,column=3)
        
        self.fieldwidgets["fieldadd_button" +str(self.row)] = tk.Button(self.updaterec_frame,textvariable=self.fieldinfo["fieldadd_var" + str(self.row)],state="normal",command=self.addFieldEntry)
        self.fieldwidgets["fieldadd_button" +str(self.row)].grid(sticky=tk.NW,row=self.row,column=4)        
                
        self.updaterec_button.grid(sticky=tk.NW,row=self.row+1,column=0)
        
    def addFieldEntry(self):
        if self.fieldinfo["fieldkey_var" + str(self.row)].get() != "" and self.fieldinfo["fieldval_var" + str(self.row)].get() != "":
            self.fieldinfo["fieldadd_var" +str(self.row)].set("Remove")            
            self.fieldwidgets["fieldadd_button" +str(self.row)].bind("<Button-1>",self.removeFieldEntry)
            self.createWidgets()
            
    def removeFieldEntry(self, event):
        removerow = event.widget.grid_info()["row"]
        
        tempwidgets = self.fieldwidgets.copy()        
        for key, val in self.fieldwidgets.items(): 
            if key.find(removerow) != -1:
                val.grid_forget()
                del tempwidgets[key]
        self.fieldwidgets = tempwidgets.copy()
        tempwidgets = {}        
        for key, val in self.fieldwidgets.items():
            if int(key[-1]) > int(removerow): 
                tempwidgets[key[:-1] + str(int(key[-1])-1)] = val                
            else:
                tempwidgets[key] = val                
        self.fieldwidgets = tempwidgets.copy()        
        
        tempinfo = self.fieldinfo.copy()        
        for key, val in self.fieldinfo.items():
            if key.find(removerow) != -1:
                del tempinfo[key]
        self.fieldinfo = tempinfo.copy()
        tempinfo = {}        
        for key, val in self.fieldinfo.items():
            if int(key[-1]) > int(removerow): 
                tempinfo[key[:-1] + str(int(key[-1])-1)] = val
            else:
                tempinfo[key] = val         
        self.fieldinfo = tempinfo.copy()        
        
        self.row = self.row - 1
        for key in self.fieldwidgets.keys():
            self.fieldwidgets[key].grid(row=int(key[-1]))
        self.updaterec_button.grid(sticky=tk.NW,row=self.row+1,column=0)
    
    def updateRecord(self):
        args = {}
        tempinfo = {}
        tempvals ={}
        tempkeys = {}
        for key, val in self.fieldinfo.items(): #Strip the fieldadd_var from self.fieldinfo to get only field key val pairs in self.fieldinfo
            if key.find("add") == -1:
                tempinfo[key] = val
        for key, val in tempinfo.items(): #Separate tempinfo items into two dicts; one with pair of (fieldkey_var*, fieldname) and the other (fieldval_var*, fieldvalue)
            if key.find("key") != -1:
                tempkeys[key] = val
            elif key.find("val") != -1:
                tempvals[key] = val
        for key_key, key_val in tempkeys.items(): #Create the arg dict of pairs (fieldname,fieldvalue) based on index value (*) of fieldkey_var* and fieldval_var*
            for val_key, val_val in tempvals.items():
                if key_key[-1] == val_key[-1]:
                    args[key_val.get()] = val_val.get()
        
        gui.DB.updateRecord(self.record_var.get(),**args)

class ViewRecordsFrame:
    def __init__(self,frame):
        self.viewrec_frame = tk.Frame(frame,height=600, width=500)
        self.viewrec_frame.grid(row=0,column=1,rowspan=3)
        self.viewrec_frame.grid_propagate(0)
        
        self.recordbyid_frame = tk.Frame(self.viewrec_frame, height=100,width=250)
        self.recordbyid_frame.grid(row=1,column=0)
        self.recordbyid_frame.grid_propagate(0)
        
        self.recordbyquery_frame = tk.Frame(self.viewrec_frame,height=100,width=250)
        self.recordbyquery_frame.grid(row=1,column=1)
        self.recordbyquery_frame.grid_propagate(0)
        
        self.createVariables()
        self.createWidgets()
    
    def createVariables(self):
        self.selectclass_menuvar = tk.StringVar()
        self.selectclass_menuvar.set("Select Class")
        self.selectclass_menuitemvar = tk.StringVar()
        
        self.getcluster_var = tk.StringVar()
        self.getcluster_var.set("Get Records for Class")
        
        self.record_menuvar = tk.StringVar()
        self.record_menuvar.set("Available Records")
        self.record_menuitemvar = tk.StringVar()
        
        self.displayrecord_var = tk.StringVar()
        self.displayrecord_var.set("Display Record")
        
        self.extendrecord_var = tk.IntVar()
        
        self.query_entryvar = tk.StringVar()        
        
        self.rectextid = int()        

    def createWidgets(self):        
        self.selectclass_menubutton = tk.Menubutton(self.viewrec_frame,relief="raised",textvariable=self.selectclass_menuvar)
        self.selectclass_menubutton.grid(sticky=tk.N,row=0,column=0)
        self.selectclass_menu = tk.Menu(self.selectclass_menubutton)
        self.selectclass_menubutton["menu"] = self.selectclass_menu
        
        self.getcluster_button = tk.Button(self.viewrec_frame, textvariable=self.getcluster_var,state="disabled",command=self.getRecords)
        self.getcluster_button.grid(sticky=tk.N,row=0,column=1)
        
        self.record_menubutton = tk.Menubutton(self.recordbyid_frame,relief="raised",textvariable=self.record_menuvar)        
        self.record_menu = tk.Menu(self.record_menubutton)
        self.record_menubutton["menu"] = self.record_menu
        
        self.displayrecord_button = tk.Button(self.recordbyid_frame, textvariable=self.displayrecord_var,command=self.displayRecord)
        
        self.extendrecord_button = tk.Checkbutton(self.recordbyid_frame,onvalue=1,text="Show Extended Record",variable=self.extendrecord_var,offvalue=0)
        
        self.deleterecord_button = tk.Button(self.recordbyid_frame,text="Delete Record", command =self.deleteRecord)
        
        self.query_entry = tk.Entry(self.recordbyquery_frame,textvariable=self.query_entryvar,width=40)
        self.query_button = tk.Button(self.recordbyquery_frame,text="Query Records",command=self.queryRecords)
        
        self.showall_button = tk.Button(self.recordbyquery_frame,text="Show All Records of Class",command=self.showAllRecords)
        
        self.canvasscroll = tk.Scrollbar(self.viewrec_frame, orient=tk.VERTICAL)        
        self.recorddisplay_canvas = tk.Canvas(self.viewrec_frame,relief=tk.RIDGE, bd=2,height=400,cursor="xterm",yscrollcommand=self.canvasscroll.set)               
        self.canvasscroll.config(command=self.recorddisplay_canvas.yview)
        self.recorddisplay_canvas.bind("<Button-1>",self.startHighlight)        
        
    def populateMenus(self):
        for item in gui.DB.ClassNames:
            self.selectclass_menu.add_checkbutton(label=item,variable=self.selectclass_menuitemvar,onvalue=item,offvalue="",command=self.updateClassButton)        
            
    def updateClassButton(self):
        if self.record_menuvar.get() != "Available Records" or self.record_menuitemvar != "": # Clear out records from menu on additional class selections after the initial selection
            self.recordIds = []
            self.record_menuvar.set("Available Records")
            self.record_menuitemvar.set("")
            self.record_menu.delete(0,self.record_menu.index(tk.END))      
            self.record_menubutton.grid_forget()
            self.displayrecord_button.grid_forget()
            self.extendrecord_var.set(0)
            self.extendrecord_button.grid_forget()
            self.deleterecord_button.grid_forget()
            self.query_entry.grid_forget()
            self.query_entryvar.set("")
            self.query_button.grid_forget()
            self.showall_button.grid_forget()
            if self.rectextid != 0: #Delete displayed record text from canvas on additional record selections after the initial
                self.recorddisplay_canvas.itemconfigure(self.rectextid,text="")
                self.recorddisplay_canvas.grid_forget()
                self.canvasscroll.grid_forget()                
                   
        self.selectclass_menuvar.set(self.selectclass_menuitemvar.get())
        self.getcluster_button["state"] = "active"
        
    def getRecords(self):
        self.recordIds = []
        if self.selectclass_menuitemvar.get() != "": 
            self.cluster = gui.DB.getCluster(self.selectclass_menuvar.get())
            for record in self.cluster["result"]:
                self.recordIds.append(record["@rid"])
            for rid in self.recordIds:
                self.record_menu.add_checkbutton(label=rid,variable=self.record_menuitemvar,onvalue=rid,offvalue="", command=self.updateRecordButton)
            self.record_menubutton.grid(sticky=tk.NW,row=0,column=0)
            self.getcluster_button["state"] = "disabled"
            self.query_entry.grid(sticky=tk.E+tk.W,row=0,column=0, columnspan=2)
            self.query_button.grid(sticky=tk.E+tk.W,row=1,column=0, columnspan=2)
            self.showall_button.grid(sticky=tk.E+tk.W,row=2,column=0, columnspan=2)
    
    def updateRecordButton(self):
        if self.rectextid != 0: #Delete displayed record text from canvas on additional record selections after the initial
            self.recorddisplay_canvas.itemconfigure(self.rectextid,text="")
            self.recorddisplay_canvas.grid_forget()
            self.extendrecord_var.set(0)
            self.canvasscroll.grid_forget()
        self.record_menuvar.set(self.record_menuitemvar.get())
        self.displayrecord_button.grid(sticky=tk.NW,row=1,column=0)
        self.extendrecord_button.grid(sticky=tk.NW,row=1,column=1)
        self.deleterecord_button.grid(sticky=tk.NW,row=2,column=0)
        self.deleterecord_button["state"] = "active"
        
        
    def displayRecord(self):
        if self.record_menuitemvar.get() != "":
            for Id in self.recorddisplay_canvas.find_all():
                self.recorddisplay_canvas.delete(Id)
            self.rectextid = self.recorddisplay_canvas.create_text(10,10,anchor=tk.NW,text=gui.DB.getRecord(self.record_menuvar.get(),self.extendrecord_var.get()))            
            self.recorddisplay_canvas.grid(sticky=tk.NW,row=2,column=0, columnspan=3)            
            self.canvasscroll.grid(sticky=tk.NE+tk.SE,row=2,column=1)
            self.recorddisplay_canvas.config(scrollregion=self.recorddisplay_canvas.bbox(tk.ALL))            
            
    def deleteRecord(self):
        self.deleterecord_button["state"] = "disabled"
        for Id in self.recorddisplay_canvas.find_all():
            self.recorddisplay_canvas.delete(Id)
        classname = self.selectclass_menuvar.get()
        recordid = self.record_menuvar.get()
        messages = gui.DB.deleteRecord(recordid,classname)
        self.updateClassButton()
        
        msgstring = "Record " + recordid + " deleted, of type " + classname + "\n"
        for message in messages:
            msgstring = msgstring + message + "\n"        
        self.recorddisplay_canvas.create_text(10,10,anchor=tk.NW,text=msgstring)
        self.recorddisplay_canvas.grid(sticky=tk.NW,row=2,column=0, columnspan=3)
        
    def queryRecords(self):
        if self.query_entryvar.get() != "":
            for Id in self.recorddisplay_canvas.find_all():
                self.recorddisplay_canvas.delete(Id)
            self.rectextid = self.recorddisplay_canvas.create_text(10,10,anchor=tk.NW,text=gui.DB.queryRecords(self.selectclass_menuvar.get(),self.query_entryvar.get()))
            self.recorddisplay_canvas.grid(sticky=tk.NW,row=2,column=0, columnspan=3)            
            self.canvasscroll.grid(sticky=tk.NE+tk.SE,row=2,column=1)
            self.recorddisplay_canvas.config(scrollregion=self.recorddisplay_canvas.bbox(tk.ALL))
            
    def showAllRecords(self):
        for Id in self.recorddisplay_canvas.find_all():
            self.recorddisplay_canvas.delete(Id)
        clustertext = json.dumps(self.cluster,sort_keys=True, indent=2, separators =(',',':'))
        self.rectextid = self.recorddisplay_canvas.create_text(10,10,anchor=tk.NW,text=clustertext)
        self.recorddisplay_canvas.grid(sticky=tk.NW,row=2,column=0, columnspan=3)            
        self.canvasscroll.grid(sticky=tk.NE+tk.SE,row=2,column=1)
        self.recorddisplay_canvas.config(scrollregion=self.recorddisplay_canvas.bbox(tk.ALL)) 
        
    def startHighlight(self,event):
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)
        specifier = "@"+str(x)+","+str(y)
        
        event.widget.select_from(self.rectextid,specifier)
        self.recorddisplay_canvas.bind("<Motion>",self.highlightText)
        self.recorddisplay_canvas.bind("<ButtonRelease>",self.endHighlight)
        
    def highlightText(self,event):
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)        
        event.widget.select_to(self.rectextid,"@%d,%d" % (x,y))        
        
    def endHighlight(self,event):
        self.recorddisplay_canvas.unbind("<Motion>")
        self.recorddisplay_canvas.unbind("<ButtonRelease>")                
        self.recorddisplay_canvas.bind("<Control-KeyPress-c>",self.copyText)
        self.recorddisplay_canvas.focus_set()       
        
    def copyText(self,event):        
        self.viewrec_frame.clipboard_clear()
        self.viewrec_frame.clipboard_append(self.recorddisplay_canvas.selection_get())       
        self.recorddisplay_canvas.unbind("<Control-KeyPress-c>")
        
        
        
        
        
        
        
        
       
             
            
            
            
        
            
gui = GuiFrame()
gui.master.title('Sample application')
gui.mainloop()       