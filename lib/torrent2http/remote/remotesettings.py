import xbmcaddon, xbmc
from . import filesystem

try: _bin_dir = xbmc.translatePath('special://home/addons/script.module.torrent2http/bin').decode('utf-8')
except: _bin_dir = xbmc.translatePath('special://home/addons/script.module.torrent2http/bin')
print(_bin_dir.encode('utf-8'))

_ADDON_NAME = 'script.module.torrent2http'
_addon = xbmcaddon.Addon(id=_ADDON_NAME)


class Settings:
    def __init__(self, path=None):
        
        self.mrsp = True if xbmc.getCondVisibility('System.HasAddon(plugin.video.romanianpack)') else False
        
        try :self.role = _addon.getSetting("role").decode('utf-8')
        except: self.role = _addon.getSetting("role")
        
        self.mrsprole = (True if self.mrgetset('experimental_server') == 'true' else False) if self.mrsp else False
        
        if self.mrsprole:
            self.storage_path  = self.mrgetset('storage')
            self.remote_host    = '0.0.0.0'
            
        else:
            try:
                self.storage_path = _addon.getSetting("storage_path").decode('utf-8')
                self.remote_host = _addon.getSetting("remote_host").decode('utf-8')
            except:
                self.storage_path = _addon.getSetting("storage_path")
                self.remote_host = _addon.getSetting("remote_host")

        self.storage_path  = filesystem.abspath(self.storage_path)
        
        try:
            self.remote_port    = int(_addon.getSetting("remote_port"))
        except:
            self.remote_port = 28282

        self.binaries_path = _bin_dir

        xbmc.log(str(self.__dict__))

    def mrgetset(self, setting):
        if self.mrsp and setting:
            return xbmcaddon.Addon(id='plugin.video.romanianpack').getSetting(setting)
        return False
