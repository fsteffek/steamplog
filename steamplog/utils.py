import datetime
import urllib2
import json


def round_datetime(a_date=datetime.datetime.now()):
    '''Round a datetime object to the nearest minute multiple of 10'''
    discard = datetime.timedelta(
            minutes=a_date.minute % 10,
            seconds=a_date.second,
            microseconds=a_date.microsecond)
    a_date -= discard
    if discard >= datetime.timedelta(minutes=5):
        a_date += datetime.timedelta(minutes=10)
    return a_date


def get_owned_games(api_key='', steam_id=''):
    """Get current playtime data from steam server return it"""
    api_url = ['https://api.steampowered.com/'
               'IPlayerService/GetOwnedGames/v0001/'
               '?include_played_free_games=1&format=json',
               '&key=', api_key,
               '&steamid=', steam_id]
    url = ''.join([url_str for url_str in api_url])
    try:
        request = urllib2.urlopen(url)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, 'We failed to reach the server.'
            print >> sys.stderr, 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, 'The server couldn\'t fulfill the request.'
            print >> sys.stderr, 'Error code: ', e.code
        sys.exit(1)
    response = json.load(request)
    return response['response']


def update_appnames_file():
    URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v2'
    try:
        request = urllib2.urlopen(URL)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, 'We failed to reach ', URL
            print >> sys.stderr, 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, 'The server couldn\'t fulfill the request.'
            print >> sys.stderr, 'Error code: ', e.code
        sys.exit(1)
    json_dict = json.load(request)
    with open('appnames.json', 'w') as a_file:
        json.dump(json_dict, a_file)
