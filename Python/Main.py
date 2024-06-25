import pickle
from shutil import copytree, copy2, rmtree
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
from functools import partial
import glob, os

class GUI:
    def __init__(self):
        r = tk.Tk()
        r.title('Steam Version Manager')
        
        self.VManager = VersionManager()
        
        self.Home = self.HomePage(r, self.VManager, self)
        self.AddGame = self.AddGamePage(r, self.VManager, self)
        
        
        self.SetShownPage(self.Home)
        
        r.mainloop()
    def SetShownPage(self, page):
        page.Show()
    class GamePart:
        def __init__(self, root, Manager, game, column=0, row=0):
            if game.Exists:
                self.TitleColor = "black"
            else:
                self.TitleColor = "red"
            self.GameFrame = tk.Frame(root)
            self.Manager = Manager
            self.Game = game
            self.column = column
            self.row = row
            self.Update()
        def Remove(self):
            self.Manager.VManager.RemoveGame(self.Game, self.var.get())
            self.Manager.Show()
        def UnSymlink(self):
            self.Manager.VManager.RemoveSymlink(self.Game, self.var.get())
            self.Manager.Show()
        def VersionCallback(self, *args):
            value = self.var.get()
            if value == self.Game.CurrentVersion:
                self.ChangeVersion["state"]="disabled"
            else:
                self.ChangeVersion["state"]="normal"
        def SwitchVersion(self):
            self.Manager.VManager.ChangeVersion(self.Game, self.var.get())
            self.Manager.Show()   
        def RunGame(self):
            print("starting: %s" % (self.Game.Location + self.CurrentExe.get()))
            os.startfile(self.Game.Location + "/"+self.CurrentExe.get())
        def Update(self):
            for i in self.GameFrame.winfo_children():
                i.destroy()
            self.Title = tk.Label(self.GameFrame, text=self.Game.Name, foreground=self.TitleColor)
            self.Title.grid(column=0, row=0)
            
            self.var = StringVar(self.GameFrame)
            self.var.set(self.Game.CurrentVersion)
            self.var.trace_add("write", self.VersionCallback)
            

            
            ButtonFrame = tk.Frame(self.GameFrame)
            print(self.Game.Versions)
            Dropdown = OptionMenu(ButtonFrame, self.var, *self.Game.Versions)
            self.VersionDrop = ttk.Combobox(ButtonFrame, state="readonly", values=self.Game.Versions, textvariable=self.var)
            #Dropdown.grid(row=0)
            self.VersionDrop.grid(row=0)
            self.ChangeVersion = tk.Button(ButtonFrame, text="Change Version", width = 15, command=self.SwitchVersion)
            self.ChangeVersion["state"]="disabled"
            self.ChangeVersion.grid(column=1, row=0)
            
            Delete = tk.Button(ButtonFrame, text="Delete", width=15, command=self.Remove)
            Edit = tk.Button(ButtonFrame, text="Edit", width=15)
            RemoveSymlink = tk.Button(ButtonFrame, text="RemoveSymlink", width=15, command=self.UnSymlink)
            if self.Game.Linked:
                pass
            else:
                RemoveSymlink["state"] = "disabled"
            ButtonFrame.grid()
            Edit.grid(column=1, row=1)
            Delete.grid(column=0, row=1)
            RemoveSymlink.grid(column=0, row=2)
            
            exes = glob.glob(self.Game.Location + "/*.exe")
            
            self.LaunchGame = tk.Button(ButtonFrame, text="Launch game", width = 15, command=self.RunGame)
            self.LaunchGame["state"]="disabled"
            
            self.CurrentExe = StringVar(ButtonFrame)
            if exes != []:
                newexes = []
                for exe in exes:
                    exe = os.path.basename(exe)
                    newexes.append(exe)
                exes = newexes
                self.CurrentExe.set(exes[0])
                self.LaunchGame["state"]="normal"
            ExeDropdown = ttk.Combobox(ButtonFrame, state="readonly", values=exes, textvariable=self.CurrentExe)
            
            ExeDropdown.grid(column=0, row=3)
            self.LaunchGame.grid(column=1, row=3)
            
            
            self.VersionCallback()
        def pack(self):
            self.Update()
            self.GameFrame.grid(column=self.column, row=self.row, padx=20, pady=20)
    class HomePage:
        def __init__(self, window, vManager, GUI):
            self.GUI = GUI
            self.window = window
            self.MaxGameColumns = 3
                        
            self.VManager = vManager
            

        def SelectSteamPath(self):
            SteamPath = filedialog.askdirectory()
            if SteamPath:
                self.VManager.SetSteamPath(SteamPath)
                
                if self.VManager.Settings["SteamPath"]:
                    self.SteamPathLabel.config(text=self.VManager.Settings["SteamPath"])
        def Show(self):
            for i in self.window.winfo_children():
                i.destroy()
            SteamPathButton = tk.Button(self.window, text='Set steam common path', width=25, command=self.SelectSteamPath)
            AddGamesButton = tk.Button(self.window, text="Add Game", width=25, command= lambda: self.GUI.SetShownPage(self.GUI.AddGame))
            self.SteamPathLabel = tk.Label(self.window, text="Not Set")  
            
            
            SteamPathButton.pack()
            self.SteamPathLabel.pack()
            self.LoadGames()
            
            AddGamesButton.pack()
            
            
            if self.VManager.Settings["SteamPath"]:
                self.SteamPathLabel.config(text=self.VManager.Settings["SteamPath"])
        def LoadGames(self): 
            GamesFrame = tk.Frame(self.window)
            GamesFrame.pack()
            i=0
            j=0
            for game in self.VManager.Games:
                Game = self.GUI.GamePart(GamesFrame, self, game, column = i, row=j)
                Game.pack()
                i+=1
                if i > self.MaxGameColumns-1:
                    i=0
                    j+=1

    
    class AddGamePage:
        def __init__(self, window, vManager, GUI):
            self.GUI = GUI
            self.window = window

            self.VManager = vManager
        def Show(self):
            for i in self.window.winfo_children():
                i.destroy()
            AddGameFrame = tk.Frame(self.window)
            AddGameFrame.pack()
            
            NameLabel = tk.Label(AddGameFrame, text="Name: ")
            NameLabel.grid(row=0)
            VersionLabel = tk.Label(AddGameFrame, text="Current Version: ")
            VersionLabel.grid(row=1)
            LocationLabel = tk.Label(AddGameFrame, text="Folder Name: ")
            LocationLabel.grid(row=2)
            
            Names = []
            for game in self.VManager.Games:
                Names.append(game.Name)
            
            self.NameSelect = ttk.Combobox(AddGameFrame, values=Names)
            self.NameSelect.grid(row=0, column=1)
            
            self.VersionEntry = tk.Entry(AddGameFrame)
            self.VersionEntry.grid(row=1, column=1)
            
            self.LocationEntry = tk.Entry(AddGameFrame)
            self.LocationEntry.grid(row=2, column=1)
            
            DoneButton = tk.Button(AddGameFrame, text="Done", width=25, command=self.Done)
            CancelButton = tk.Button(AddGameFrame, text="Cancel", width=25, command=self.Cancel)
            
            DoneButton.grid(column=1, row = 3)
            CancelButton.grid(column=0, row = 3)
        def Done(self):
            name = self.NameSelect.get()
            version = self.VersionEntry.get()
            location = self.LocationEntry.get()
            if version == "" or name == "":
                return
            for game in self.VManager.Games:
                if game.Name == name:
                    self.VManager.AddVersion(game, version, location)
                    self.Cancel()
                    return
            self.VManager.AddGame(name, version, location)
            self.Cancel()
        def Cancel(self):
            self.GUI.SetShownPage(self.GUI.Home)

        
class VersionManager:
    
    def __init__(self):
        print(os.path.dirname(__file__))
        self.SavePath = os.path.dirname(__file__) + "\settings.pickle"
        self.GamesPath = os.path.dirname(__file__) + "\games.pickle"
        self.Settings = {
            "SteamPath" : None
        }
        self.Games = []
        self.GetSettings()
        self.LoadGames()
    def AddVersion(self, Game, Version, Location = ""):
        if Location == "":
            Location = Game.Location
        else:
            Location = self.Settings["SteamPath"] + "/" + Location
        if Game.Exists:
            Destination = "%s\Games\%s - %s" % (os.path.dirname(__file__),Game.Name, Version)
            print(Location)
            print(Destination)
            def copy2_verbose(src, dst):
                print('Copying {0}'.format(src))
                copy2(src,dst)
            copytree(Location, Destination, copy_function=copy2_verbose)
            self.ChangeVersion(Game, Version)
        
        Game.Versions.append(Version)
        Game.CurrentVersion = Version
        self.SaveToFile(self.GamesPath, self.Games)
    def ChangeVersion(self, Game, Version):
        if Game.Exists:
            if Game.Linked:
                self.RemoveSymlink(Game, Game.CurrentVersion)
            rmtree(Game.Location)
            self.CreateSymlink(Game, Version)
            Game.CurrentVersion = Version
            Game.Linked = True
            self.SaveToFile(self.GamesPath, self.Games)
    def CreateSymlink(self, Game, Version):
        Destination = "%s\Games\%s - %s" % (os.path.dirname(__file__),Game.Name, Version)
        os.symlink(Destination, Game.Location)
    def RemoveSymlink(self, Game, CurrentVersion):
        if Game.Exists:
            try:
                os.unlink(Game.Location)
            except:
                print("Not Linked")
            Game.Linked = False
            Game.CurrentVersion = ""
            CurrentLocation = "%s\Games\%s - %s" % (os.path.dirname(__file__),Game.Name, CurrentVersion)
            def copy2_verbose(src, dst):
                print('Copying {0}'.format(src))
                copy2(src,dst)
            try:
                copytree(CurrentLocation, Game.Location, copy_function=copy2_verbose)
            except:
                print("Cant Copy")
            self.SaveToFile(self.GamesPath, self.Games)
        
        
    def AddGame(self, Name, Version, Location):
        if Location == "":
            Location = None
        else:
            Location = self.Settings["SteamPath"] + "/" +Location
        game = self.Game(Name, Location=Location)
        self.AddVersion(game, Version)
        self.Games.append(game)
        self.SaveToFile(self.GamesPath, self.Games)
    def RemoveGame(self, game, version ):
        if version == game.CurrentVersion:
            self.RemoveSymlink(game, version)
        game.Versions.remove(version)
        Destination = "%s\Games\%s - %s" % (os.path.dirname(__file__),game.Name, version)
        
        if game.Versions == []:
            self.Games.remove(game)
        rmtree(Destination)
        self.SaveToFile(self.GamesPath, self.Games)
    def LoadGames(self):
        games = self.LoadFromFile(self.GamesPath)
        if games:
            for game in games:
                print(game.Name)
            self.Games = games   
    
    def SetSteamPath(self, Path):
        self.Settings["SteamPath"] = Path
        self.SaveToFile(self.SavePath, self.Settings)
        
    def SaveToFile(sefl, Path, Data):   
        with open(Path, "wb") as file:
            pickle.dump(Data, file) 
    
    def LoadFromFile(self, path):
        try:
            with open(path, "rb") as file:
                return pickle.load(file)            
        except Exception as error:
            print("an exception occurred: ", error)
            return None       
    def GetSettings(self):

        TempSettings = {}
        
        TempSettings = self.LoadFromFile(self.SavePath)
        if TempSettings:
            for k, v in TempSettings.items():
                self.Settings[k] = v
                
    class Game:
        def __init__(self, Name, Versions=[], Location=None):
            
            self.Name = Name
            self.Versions = Versions
            self.CurrentVersion = None
            self.Location = Location
            self.Linked = False
            if Location:
                self.Exists = os.path.exists(Location)
            else:
                self.Exists = False



            
if __name__ == "__main__":
    gui = GUI()
