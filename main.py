import xbmcgui
import xbmcplugin
import json
import logger as Logger
import addon as Addon
import vectra as Vectra


class Main:
    log = Logger.Logger(__name__)
    addon = Addon.Addon()
    vectra = Vectra.Vectra()

    def __init__(self):
        if self.check_connection():
            self.stations = sorted(json.loads(self.vectra.load_stations()))
            self.display_stations()

    def check_connection(self):
        if self.vectra.restore_session():
            self.log.i('Session restored successfully.')
            return True
        else:
            self.vectra.register_new_device()
            if self.vectra.devices_count() > self.vectra.MAX_DEVICES:
                self.log.i(
                    'Too many devices! Go to http://tvonline.vectra.pl/urzadzenia/ and manually remove unused devices.')
                self.addon.show_ok_dialog(
                    'Masz zbyt wiele zarejestrowanych urzadzen (max. 3).\n\nWejdz na  http://tvonline.vectra.pl/urzadzenia/  i usun z listy nieuzywane urzadzenia.')
                self.vectra.delete_current_session()
                return False
            else:
                self.log.i('New device added successfully.')
                self.vectra.clear_stations()
                self.addon.show_notification('Dodano nowe urzadzenie. Pobieram stacje...', 6000)
                return True

    def display_stations(self):
        xbmcplugin.setContent(self.addon.HANDLE, 'movies')
        for station in self.stations:
            try:
                li = xbmcgui.ListItem(station['name'], iconImage='DefaultVideo.png')
                url = station['stream_url']
                if url:
                    xbmcplugin.addDirectoryItem(self.addon.HANDLE, url=url, listitem=li)
            except:
                pass
        xbmcplugin.endOfDirectory(self.addon.HANDLE)

main = Main()
