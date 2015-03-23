import datetime
import urllib2
import json
import sys


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


def get_app_list():
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
    return [(app['appid'], app['name'])
            for app in json_dict['applist']['apps']]


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
## https://stackoverflow.com/questions/3160699/python-progress-bar/158607
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
