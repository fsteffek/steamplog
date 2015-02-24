#!/usr/bin/python
# File: steam.py
# Description: This script downloads the playtime data of player `steam_id`
#              and saves it into a MySQL database.
# Documentation: 06.02.2015

import sys
import argparse
import json
import time, datetime
import MySQLdb
import urllib2

def reset_config():
    json_ = json.dumps({'API key': 'Insert API key',
                        'Steam ID': 'Insert Steam ID',
                       },
            sort_keys=True, indent=4, separators=(',', ': '))
    with open('config.json', 'w') as file_:
        file_.write(json_)

def read_config():
    with open('config.json', 'r') as file_:
        json_ = json.load(file_)
    return (json_['API key'], json_['Steam ID'])

def update_appnames_file():
    try:
        request = urllib2.urlopen('http://api.steampowered.com/ISteamApps/GetAppList/v2')
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, 'We failed to reach ', url
            print >> sys.stderr, 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, 'The server couldn\'t fulfill the request.'
            print >> sys.stderr, 'Error code: ', e.code
        sys.exit(1)
    ajson = json.load(request)
    with open('appnames.json', 'w') as afile:
        json.dump(ajson, afile)

def read_appnames_file():
    filename = 'appnames.json'
    try:
        afile = open(filename, 'r')
        ajson = json.load(afile)
        afile.close()
    except IOError, ValueError:
        print >> sys.stderr, 'Could not read ', filename
    appnames = {}
    for app in ajson['applist']['apps']:
        appnames[ str(app['appid']) ] = app['name']
    return appnames


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

    # Create request url
    url  = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    url += '?include_played_free_games=1&format=json&key=' + api_key
    url += '&steamid=' + steam_id
    if options.verbose:
        print 'Connecting to ' + url
    if options.dry_run:
        sys.exit(0)

    # Request data from Steam server and get a file-like object
    try:
        request = urllib2.urlopen( url )
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, 'We failed to reach the server.'
            print >> sys.stderr, 'Reason: ', e.reason
            sys.exit(1)
        elif hasattr(e, 'code'):
            print >> sys.stderr, 'The server couldn\'t fulfill the request.'
            print >> sys.stderr, 'Error code: ', e.code
            sys.exit(1)

    # Decode the request from `file-like object` into json
    json_data = json.load(request)

    if options.pretty_print:
        print json.dumps(json_data, indent=4, separators=(',', ': '))
        sys.exit(0)
    if options.print_only:
        print json_data
        sys.exit(0)

    # Get timestamp to save into database
    time_in_unix = int( time.time() )

    # MySQL data
    db = MySQLdb.connect( host = "localhost"
                        , user = "steam"
                        , db = "steam" )
    # Execute a SQL QUERY using the execute method
    cursor = db.cursor()

    # Crunch data
    for game in json_data['response']['games']:
        query = 'INSERT INTO ' + table
        query += ' ( appid, minutes_played, time_of_record ) VALUES ( '
        query += '%d, ' % game.get('appid', 0)
        query += '%d, ' % game.get(table, 0)
        query += '%d )' % time_in_unix

        if options.verbose:
            print query

        cursor.execute( query )

    # Make changes permanent
    db.commit()
    # Disconnect from MySQL server
    db.close()

def makeParser():

    parser = argparse.ArgumentParser(prog='steamplaytime', add_help=False)
    parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true',
                        help='do not connect to steam server')
    parser.add_argument('-p', '--print-only', dest='print_only', action='store_true',
                        help='print current playtime data and exit')
    parser.add_argument('-P', '--pretty-print', dest='pretty_print', action='store_true',
                        help='like -p but print it in a human-readable format')
    parser.add_argument('--reset-config', dest='reset_config', action='store_true',
                        help='remove sensitive data from config.json')
    parser.add_argument('--update-apps', dest='update_appnames', action='store_true',
                        help='get new apps list from steam (for app names)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-h', '--help', dest='help', action='store_true',
                        help='show this help message and exit')
    return parser


if __name__ == "__main__":
    main()
