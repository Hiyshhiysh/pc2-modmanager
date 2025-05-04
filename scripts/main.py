import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font as tkf
import tkinter.filedialog as tkfd
import modManager
import os

os.chdir(os.path.abspath(os.path.dirname(__file__)))

manager = modManager.Manager()

class MainPanel(tk.Frame):

    modDetails = []
    
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent

        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        
        self.ListBox = tk.Listbox(self)
        self.ListBox.grid(row=0,column=0,rowspan=2,sticky="nesw")
        self.ListBox.bind("<<ListboxSelect>>",self.modSelected)

        self.detailsPanel = ModDetailsPanel(self)

        self.actionsBar = ModActionsBar(self)
        self.actionsBar.grid(row=1,column=1,sticky="ew",padx=5,pady=(0,10))

    def directoryLoaded(self):
        self.actionsBar.setBarEnabled(True)

    def closeGame(self):
        self.detailsPanel.grid_forget()
        self.actionsBar.setBarEnabled(False)
        
    def refresh(self):

        self.modDetails = manager.getModDetails()
        
        self.ListBox.delete(0,tk.END)
        self.ListBox.insert(tk.END,*[item["name"] for item in self.modDetails])
        
        self.ListBox.select_set(0)
        self.ListBox.event_generate("<<ListboxSelect>>")

    def modSelected(self,event):
        selectedMod = self.getSelectedModDetails()
        if not selectedMod: return
        self.detailsPanel.grid(row=0,column=1, sticky="nesw",padx=10,pady=10)
        self.detailsPanel.setData(selectedMod)
        self.actionsBar.setSelectedMod(selectedMod)

    def modEnabledToggled(self,enabled):
        if enabled:
            self.detailsPanel.title.configure(fg="#000000")
        else:
            self.detailsPanel.title.configure(fg="#aaaaaa")

    def getSelectedModDetails(self):
        selectedModIndex = next(iter(self.ListBox.curselection()),None)
        if selectedModIndex == None: return
        return self.modDetails[selectedModIndex]
        
    def setItems(self,items):
        pass
        

class ModDetailsPanel(tk.Frame):

    currentModId = ""
    
    def __init__(self,parent):
        super().__init__(parent,
            bd=2,relief="groove",
            padx=10,pady=10)

        self.parent=parent

        self.grid_columnconfigure(0,weight=1)

        self.titleBar = tk.Frame(self)
        self.titleBar.grid(row=0,column=0,sticky="nesw")
        self.titleBar.grid_columnconfigure(0,weight=1)

        self.title = tk.Label(self.titleBar,text="hello",font=("TkTextFont",20), anchor="w")
        self.title.grid(row=0,column=0,sticky="w")

        self.titleSeparator = ttk.Separator(self,orient="horizontal")
        self.titleSeparator.grid(row=1,column=0,sticky="ew",pady=(15,10))

        self.modIcon = tk.PhotoImage()
        
        self.img = tk.Label(self.titleBar,image=self.modIcon,bd=3,relief="sunken")
        self.img.grid(row=0,column=1,sticky="e")

        self.desc = tk.Message(self,text="description lol",anchor="nw",justify="left")
        self.desc.bind("<Configure>", lambda e: self.desc.config(width=e.width))
        self.desc.grid(row=2,column=0,sticky="nesw")

    def setData(self,modDetails):
        self.currentModId = modDetails["id"]
        self.title.configure(text=modDetails["name"])
        self.desc.configure (text=modDetails["desc"])
        if modDetails["img"] == "":
            self.modIcon = tk.PhotoImage(file="../assets/placeholder.png")
        else:
            self.modIcon = tk.PhotoImage(data=modDetails["img"])
        self.img.configure(image=self.modIcon)

        if manager.getModEnabled(modDetails["id"]):
            self.title.configure(fg="#000000")
        else:
            self.title.configure(fg="#aaaaaa")

    def refresh():
        return self.parent.refresh()

class TopBar(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        
        self.grid_columnconfigure(0,weight=1)

        self.configure(bd=2,relief="groove")

        self.statusLabel = tk.Label(self,text="",anchor="w")
        self.statusLabel.grid(row=0,column=0,sticky="w")

        # Select directory buttons
        
        self.selectDirectoryButton = tk.Button(self,text="Select Game Directory",command=self.selectDirectoryClicked)
        self.autoDetectButton = tk.Button(self,text="Auto-detect PC2 Directory",command=self.autoDetectClicked)

        # Mods options buttons

        self.installModButton = tk.Button(self,text="Install Mod",command=self.installModClicked)
        self.refreshButton = tk.Button(self,text="Refresh",command=self.refreshClicked)
        self.closeGameButton = tk.Button(self,text="Close Game",command=self.closeGameClicked)

        self.switchTopBar(0)

    def selectDirectoryClicked(self):
        path = tkfd.askdirectory(mustexist=True)
        if path=="":return
        success = manager.setInstallPath(path)
        if success == 0: self.parent.directoryLoaded()

    def autoDetectClicked(self):
        success = manager.autoDetectInstallPath()
        if success == 0: self.parent.directoryLoaded()

    def installModClicked(self):
        path = tkfd.askopenfilename(filetypes=[("Zip Files",".zip")])
        if path=="":return
        success = manager.installMod(path)
        if success == 0: self.parent.directoryLoaded()

    def refreshClicked(self):
        self.parent.refreshModList()

    def closeGameClicked(self):
        self.switchTopBar(0)
        self.parent.closeGame()
        manager.closeGame()
        self.parent.refreshModList()

    def directoryLoaded(self):
        self.parent.refreshModList()
        self.switchTopBar(1)

    def switchTopBar(self,num):
        if num == 0:

            self.statusLabel.configure(text="No game loaded")
            
            self.installModButton.grid_forget()
            self.refreshButton.grid_forget()
            self.closeGameButton.grid_forget()
            
            self.selectDirectoryButton.grid(row=0,column=1)
            self.autoDetectButton.grid(row=0,column=2)
            
        elif num == 1:

            self.statusLabel.configure(text=f"Game Loaded: {manager.getGameName()}")
            
            self.selectDirectoryButton.grid_forget()
            self.autoDetectButton.grid_forget()
            
            self.installModButton.grid(row=0,column=1)
            self.refreshButton.grid(row=0,column=2)
            self.closeGameButton.grid(row=0,column=3)

class ModActionsBar(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent

        self.modDetails = None
        
        self.deleteButton = tk.Button(self,text="Delete",width=10,command=self.deleteClicked)
        self.deleteButton.grid(row=0,column=0,padx=5,sticky="w")

        self.toggleEnabledButton = tk.Button(self,text="Disable",width=10,command=self.toggleModEnabled)
        self.toggleEnabledButton.grid(row=0,column=1,padx=5,sticky="w")

        self.setBarEnabled(False)

        self.modEnabled = None

    def setSelectedMod(self,modDetails):
        self.modDetails = modDetails
        self.modEnabled = manager.getModEnabled(self.modDetails.get("id"))
        self.toggleEnabledButton.config(text=self.modEnabled and "Disable" or "Enable")
            

    def deleteClicked(self):
        if tk.messagebox.askokcancel(title="PC2 Mod Manager",message=f"Are you sure you want to delete {self.modDetails['name']}?"):
            manager.uninstallMod(self.modDetails["id"])
            self.parent.refresh()
    
    def toggleModEnabled(self):
        print(not self.modEnabled)
        manager.setModEnabled(self.modDetails["id"],not self.modEnabled)
        self.modEnabled = not self.modEnabled
        self.toggleEnabledButton.config(text=self.modEnabled and "Disable" or "Enable")
        self.parent.modEnabledToggled(self.modEnabled)

    def setBarEnabled(self,enabled):
        state = enabled and "normal" or "disabled"
        self.deleteButton.config(state=state)
        self.toggleEnabledButton.config(state=state)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("700x500")
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)

        self.topbar = TopBar(self)
        self.topbar.grid(row=0,column=0,sticky="nesw")

        self.mainContent = MainPanel(self)
        self.mainContent.grid(row=1,column=0,sticky="nesw")

    def refreshModList(self):
        self.mainContent.refresh()

    def closeGame(self):
        self.mainContent.closeGame()

    def directoryLoaded(self):
        self.mainContent.directoryLoaded()
        self.topbar.directoryLoaded()
            

root = App()

root.mainloop()
