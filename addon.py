import sys
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import os
import cookielib
import logger


class Addon:
    # Addon info:
    ADDON = xbmcaddon.Addon('plugin.video.vectra.tvonline')
    VERSION = ADDON.getAddonInfo('version')
    ID = ADDON.getAddonInfo('id')
    NAME = ADDON.getAddonInfo('name')
    ICON = ADDON.getAddonInfo('icon')
    PATH = ADDON.getAddonInfo('path')
    HANDLE = int(sys.argv[1])

    # Disk paths:
    _SEP = os.path.sep
    _PATH_RESOURCES = PATH + _SEP + 'resources'
    _PATH_TMP = PATH + _SEP + 'tmp'

    def __init__(self):
        self.log = logger.Logger(__name__)

    def path_resources(self):
        """ Returns path to resource folder. Creates it if it does not exist. """
        if not xbmcvfs.exists(self._PATH_RESOURCES):
            xbmcvfs.mkdir(self._PATH_RESOURCES)
        return self._PATH_RESOURCES + self._SEP

    def path_tmp(self):
        """ Returns path to temporary folder. Creates it if it does not exist. """
        if not xbmcvfs.exists(self._PATH_TMP):
            xbmcvfs.mkdir(self._PATH_TMP)
        return self._PATH_TMP + self._SEP

    def cookie_jar(self):
        return cookielib.LWPCookieJar(self.path_tmp() + 'cookies.txt')

    def clear_cookies(self):
        self.delete_file(self.path_tmp() + 'cookies.txt')

    def write_file(self, path, value):
        """ Writes value to a file. """
        try:
            f = xbmcvfs.File(path, 'w')
            f.write(value)
            f.close()
        except:
            self.log.e('Error while writing to file - ' + path)

    def read_file(self, path):
        """ Reads value from a file. """
        try:
            f = xbmcvfs.File(path)
            b = f.read()
            f.close()
            return b
        except:
            self.log.e('Error while reading file - ' + path)
            return ""

    def delete_file(self, path):
        """ Deletes file. """
        try:
            xbmcvfs.delete(path)
        except:
            self.log.e('Error while deleting file - ' + path)

    def exists(self, path):
        """ Checks if path exists. """
        return xbmcvfs.exists(path)

    def show_notification(self, msg, timemillis):
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (self.NAME, msg, timemillis, self.ICON))

    def show_ok_dialog(self, msg):
        xbmcgui.Dialog().ok(self.NAME, msg)
