import requests
import json
import addon as Addon
from BeautifulSoup import BeautifulSoup as Soup


class Vectra:
    URL = 'http://tvonline.vectra.pl'
    DEVICE_NAME = 'KodiPlugin'
    MAX_DEVICES = 3

    def __init__(self):
        self.addon = Addon.Addon()
        self.cookie_jar = self.addon.cookie_jar()
        self.session = requests.Session()
        self.session.cookies = self.cookie_jar
        self.path_stations = self.addon.path_resources() + 'stations.txt'
        self.devices = []

    def restore_session(self):
        """ Tries to restore session.
            Returns false when session couldn't be restored which means that new device has to be registered. """
        try:
            self.cookie_jar.load()
            if self._session_expired():
                return False
            else:
                return True
        except:
            return False

    def register_new_device(self):
        self._accept_license()
        self._add_new_device()
        self._save_session()
        self.devices = self._get_devices_list()

    def devices_count(self):
        return len(self.devices)

    def delete_current_session(self):
        kodi_devices = []
        for device in self.devices:
            if device['name'].startswith(self.DEVICE_NAME):
                kodi_devices.append(device)
        self._delete_device(kodi_devices[-1]['delete_url'])
        self.addon.clear_cookies()

    def load_stations(self):
        """ Reads stations from a text file. """
        if not self.addon.exists(self.path_stations):
            self._save_stations(self._get_stations())

        return self.addon.read_file(self.path_stations)

    def clear_stations(self):
        self.addon.delete_file(self.path_stations)

    def _accept_license(self):
        """ Accept license agreement. """
        self.session.post(self.URL, data={'policy_accept': 'on'})

    def _add_new_device(self):
        """ Adds new device. """
        self.session.post(self.URL + '/urzadzenia/nowe/', data={'name': self.DEVICE_NAME})

    def _save_session(self):
        """ Saves cookies on disk. """
        self.session.cookies.save(ignore_discard=True)

    def _session_expired(self):
        """ Checks if session expired (based on number of registered devices). """
        self.devices = self._get_devices_list()
        if not self.devices:
            # no devices means that we don't have an access to the devices page -> session expired
            return True
        else:
            return False

    def _delete_device(self, url):
        """ Deletes device from Vectra page. """
        self.session.get(url)

    def _get_devices_list(self):
        """ Retrieves list of devices from your Vectra page. """
        r = self.session.get(self.URL + '/urzadzenia')
        html_devices = Soup(r.content).findAll('a', {'class': 'device-delete'})
        names = []
        delete_urls = []

        for device in html_devices:
            names.append(device.parent.contents[0].strip()[:-1].strip())
            delete_urls.append(self.URL + device['href'])

        return [{'name': name, 'delete_url': delete_url}
                for name, delete_url in zip(names, delete_urls)]

    def _get_stations(self):
        """ Returns json with list of tv stations.
            Json includes station's name, id, get url and direct stream url. """
        r = self.session.get(self.URL)
        html_stations = Soup(r.content).find(id='station-list').find('ul')

        ids = []
        names = []
        get_urls = []
        stream_urls = []

        for station in html_stations.findAll('li'):
            id = station.a['href'].replace('#', '').replace('error-package', '')
            name = station.h2.string
            get_url = 'http://tvonline.vectra.pl/player/params/?os=ios&station=' + id
            stream_url = self._get_stream_url(get_url)

            ids.append(id)
            names.append(name)
            get_urls.append(get_url)
            stream_urls.append(stream_url)

        return json.dumps(
                [{'id': id, 'name': name, 'get_url': get_url, 'stream_url': stream_url}
                 for id, name, get_url, stream_url in zip(ids, names, get_urls, stream_urls)], indent=4, sort_keys=True
        )

    def _get_stream_url(self, get_url):
        """ Get direct stream url based on get_url. """
        r = self.session.get(get_url, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=30)
        try:
            return r.json()['url']
        except:
            if r.status_code == 200:
                if r.content.startswith('Throttled'):
                    return self._get_stream_url(get_url)  # retry
            return ""

    def _save_stations(self, stations_json):
        """ Save stations to a text file. """
        self.addon.write_file(self.path_stations, stations_json)
