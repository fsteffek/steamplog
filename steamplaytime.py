#!/usr/bin/python
# File: steam.py
# Description: This script downloads the playtime data of player `steam_id`
#              and saves it into a MySQL database.
# Documentation: 06.02.2015

import sys
import argparse
import json
import time
import datetime
import MySQLdb
import urllib2

from steamplaytime.app import App


def main():
    global options
    parser = makeParser()
    options = parser.parse_args(sys.argv[1:])
    if options.help:
        parser.print_help()
        sys.exit(0)
    if options.reset_config:
        reset_config()
    if options.update_appnames:
        update_appnames_file()
    if options.reset_config or options.update_appnames:
        sys.exit(0)

    (api_key, steam_id) = read_config()

    owned_games = get_owned_games(api_key, steam_id)

    if options.pretty_print:
        print json.dumps(owned_games, indent=4, separators=(',', ': '))
        sys.exit(0)
    if options.print_only:
        print owned_games
        sys.exit(0)

    # MySQL data
    db = MySQLdb.connect(
            host="localhost",
            user="steam",
            db="steam")
    # Execute a SQL QUERY using the execute method
    cursor = db.cursor()

    if options.save:
        save_to_db(cursor, owned_games)

    # Disconnect from MySQL server
    db.close()


def save_to_db(cursor, owned_games):
    """Insert playtime data into database"""
    time_in_unix = int(time.time())  # timestamp for db
    for game in owned_games['games']:
        query = 'INSERT INTO ' + table
        query += ' ( appid, minutes_played, time_of_record ) VALUES ( '
        query += '%d, ' % game.get('appid', 0)
        query += '%d, ' % game.get(table, 0)
        query += '%d )' % time_in_unix
        cursor.execute(query)
    db.commit()


def app_ids_from_db(cursor):
    """Get the app id for each game in database and return as list"""
    query = 'SELECT DISTINCT appid FROM playtime_forever ORDER BY appid'
    cursor.execute(query)
    table = cursor.fetchall()  # returns a tuple of tuples
    return [row[0] for row in table]


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


def reset_config():
    json_str = json.dumps(
            {'API key': 'Insert API key',
             'Steam ID': 'Insert Steam ID'},
            sort_keys=True, indent=4, separators=(',', ': '))
    with open('config.json', 'w') as a_file:
        a_file.write(json_str)


def read_config():
    with open('config.json', 'r') as a_file:
        json_dict = json.load(a_file)
    return (json_dict['API key'], json_dict['Steam ID'])


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


def read_appnames_file():
    filename = 'appnames.json'
    try:
        a_file = open(filename, 'r')
        json_dict = json.load(a_file)
        a_file.close()
    except IOError, ValueError:
        print >> sys.stderr, 'Could not read ', filename
    app_names = {}
    for app in json_dict['applist']['apps']:
        app_names[str(app['appid'])] = app['name']
    return app_names


def makeParser():
    parser = argparse.ArgumentParser(prog='steamplaytime', add_help=False)
    # parser.add_argument(
    #         '-n', '--dry-run', dest='dry_run', action='store_true',
    #         help='do not connect to steam server')
    parser.add_argument(
            '-p', '--print-only', dest='print_only', action='store_true',
            help='print current playtime data and exit')
    parser.add_argument(
            '-P', '--pretty-print', dest='pretty_print', action='store_true',
            help='like -p but print it in a human-readable format')
    parser.add_argument(
            '--reset-config', dest='reset_config', action='store_true',
            help='remove sensitive data from config.json')
    parser.add_argument(
            '--save', dest='save', action='store_true',
            help='record new playtime into database')
    parser.add_argument(
            '--update-apps', dest='update_appnames', action='store_true',
            help='get new apps list from steam (for app names)')
    parser.add_argument(
            '-v', '--verbose', dest='verbose', action='store_true',
            help='be verbose')
    parser.add_argument(
            '-h', '--help', dest='help', action='store_true',
            help='show this help message and exit')
    return parser


if __name__ == "__main__":
    main()
