import os
import pathlib as pl
import zipfile as zf
import shutil as sh
import json
import os

class Manager:
    _gameDirectory = None
    _ovldataPath = None
    
    def __init__(self):
        pass
    
    def setInstallPath(self,pathStr):
        path = pl.Path(pathStr)
        if path.exists():
            try:
                ovldataPath = next(path.rglob("*/ovldata"))
                self._ovldataPath = ovldataPath
            except:
                return 2
            self._gameDirectory = path
            return 0
        else:
            return 1
        
    def autoDetectInstallPath(self):
        for path in [
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Planet Coaster 2",
            "C:\\Program Files\\Epic Games\\Planet Coaster 2"
        ]: # aw man, he sad
            result = self.setInstallPath(path)
            if result == 0: return 0
        return 1

    def closeGame(self):
        self._gameDirectory = None
        self._ovldataPath = None

    def getGameName(self):
        return self._gameDirectory.name

    def getModList(self):
        if not self._ovldataPath: return []
        return [item.name for item in self._ovldataPath.iterdir() if item.name != "GameMain" and not item.name.startswith("Content")]

    def getModDetails(self):
        modIds = self.getModList()
        modDetailsList = []

        for modId in modIds:
            modDetails = {
                "id":modId,
                "name":modId,
                "desc":"No description.",
                "img":""
            }
            
            modDetailsDirectory = self._ovldataPath / modId / "modinfo.json"
            if modDetailsDirectory.exists():
                try:
                    with open(modDetailsDirectory) as modDetailsFile:
                        modDetailsJson = json.load(modDetailsFile)
                        assert not modDetailsJson.get("id")
                        modDetails = modDetails | modDetailsJson
                except:
                    modDetails["desc"] = "An unexpected error occured when trying to load the details for this mod."
            
                
            modDetailsList.append(modDetails)

        return modDetailsList
                
                
        
        return [{"name":modId,"desc":"","img":""} for modId in modIds]

    def getModPath(self,modId):
        return self._ovldataPath / modId
            
    def installMod(self,path):
        #if not self._ovldataPath: return 1
        #try:
            with zf.ZipFile(path) as modZip:
                modZip.extractall(self._ovldataPath)
            return 0
        #except:
        #    return 2

    def uninstallMod(self,modId):
        sh.rmtree(self.getModPath(modId))

    def getModEnabled(self,modId):
        modDirectory = self._ovldataPath / modId
        if modDirectory.exists():
            return not bool(next(modDirectory.rglob("_disabled_*.ovl"),False))

    def setModEnabled(self,modId,enabled):
        modDirectory = self._ovldataPath / modId
        if modDirectory.exists():
            if enabled:
                for ovlfile in modDirectory.rglob("*.ovl"):
                    print(ovlfile.name)
                    ovlfile.rename(ovlfile.with_name(ovlfile.name.removeprefix("_disabled_")))
                    
            else:
                for ovlfile in modDirectory.rglob("*.ovl"):
                    print(ovlfile.name)
                    if ovlfile.name.startswith("_disabled_"): continue
                    ovlfile.rename(ovlfile.with_name("_disabled_"+ovlfile.name))
                    print(ovlfile)
                    
            
