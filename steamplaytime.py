#!/usr/bin/python
# File: steam.py
# Description: This script downloads the playtimer data of player `steam_id`
#              and saves it into a MySQL database.
# Documentation: 06.02.2015

import getopt, sys
import json
import time, datetime
import MySQLdb
import urllib2

from SteamPlaytimeSecret import api_key, steam_id

def main():
    try:
        # https://docs.python.org/2/library/getopt.html
        opts, args = getopt.getopt(sys.argv[1:], "hnv")
    except getopt.GetoptError as err:
        # print help information and exit
        print str(err)
        usage()
        sys.exit(2)
    verbose = False
    dry_run = False
    for o, a in opts:
        if o == "-n":
            dry_run = True
        elif o == "-h":
            usage()
            sys.exit(0)
        elif o == "-v":
            verbose = True
        else:
            print >> sys.stderr, 'Unhandled option: ', o
            usage()
            sys.exit(2)

    # Create request url
    url  = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    url += '?include_played_free_games=1&format=json&key=' + api_key
    url += '&steamid=' + steam_id
    if verbose:
        print 'Connecting to ' + url
    if dry_run:
        sys.exit(0)

    # Request data from Steam server and get a file-like object
    try:
        request = urllib2.urlopen( url )
    except URLError, e:
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

        if verbose:
            print query

        cursor.execute( query )

    # Make changes permanent
    db.commit()
    # Disconnect from MySQL server
    db.close()


if __name__ == "__main__":
    main()
