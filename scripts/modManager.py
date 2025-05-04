import os
import pathlib as pl
import zipfile as zf
import shutil as sh

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

    def getModDetails(self,modId):
        return None

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
