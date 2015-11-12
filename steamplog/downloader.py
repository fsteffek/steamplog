from __future__ import print_function
import sys
import json
import urllib2


class Downloader(object):
    '''Download data via Steam-API'''
    def __init__(self, api_key):
        self.API = api_key

    def download_stats(self, steam_id):
        '''Download owned games from Steam Web API'''
        URL = ['https://api.steampowered.com/'
               'IPlayerService/GetOwnedGames/v0001/'
               '?include_played_free_games=1&format=json',
               '&key=', self.API,
               '&steamid=', steam_id]
        URL = ''.join([url_str for url_str in URL])
        try:
            request = urllib2.urlopen(URL)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print('We failed to reach the server.', file=sys.stderr)
                print('Reason: ', e.reason, file=sys.stderr)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.',
                      file=sys.stderr)
                print('Error code: ', e.code, file=sys.stderr)
            sys.exit(1)
        response = json.load(request)
        if "games" not in response['response']:
            print >> sys.stderr, 'ERROR: No games found'
            sys.exit(1)
        else:
            return response['response']['games']

    def download_applist(self):
        '''Download app names dictionary and return as list'''
        URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v2'
        try:
            request = urllib2.urlopen(URL)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print('We failed to reach ', URL, file=sys.stderr)
                print('Reason: ', e.reason, file=sys.stderr)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.',
                      file=sys.stderr)
                print('Error code: ', e.code, file=sys.stderr)
            sys.exit(1)
        json_dict = json.load(request)
        return [(app['appid'], app['name'])
                for app in json_dict['applist']['apps']]
