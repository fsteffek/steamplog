#!/usr/bin/python
# File: steamplog.py
# Description: Steamplog logs and plots yout playtime on steam

import sys
import argparse
import json
import time
import datetime

from steamplog.app import App
from steamplog.db import steamplog_db
import steamplog.plot as plot
import steamplog.utils as utils


def main(argv=None):
    if argv is None:
        argv = sys.argv
    global options
    global application_name
    application_name = argv[0]
    parser = makeParser()
    options = parser.parse_args(argv[1:])
    if options.help:
        parser.print_help()
        sys.exit(0)
    if options.reset_config:
        reset_config()
    if options.update_appnames:
        utils.update_appname(utils.get_app_list())
    if options.reset_config or options.update_appnames:
        sys.exit(0)
    if not options.filename:
        options.filename = 'output.png'

    db = steamplog_db()

    db.configure()

    if options.plot:
        makePlot(db)
        sys.exit(0)

    (api_key, steam_id) = read_config()

    owned_games = utils.get_owned_games(api_key, steam_id)

    if 'games' not in owned_games:
        print >> sys.stderr, application_name + ': NOTICE: No games found'
        sys.exit(0)

    if options.pretty_print:
        print json.dumps(owned_games, indent=4, separators=(',', ': '))
        sys.exit(0)
    if options.print_only:
        print owned_games
        sys.exit(0)

    if options.save:
        db.log_playtime(owned_games)

    # Disconnect from database
    db.close()


def reset_config():
    json_str = json.dumps(
            {'API key': 'YourKey',
             'Steam ID': 'YourID'},
            sort_keys=True, indent=4, separators=(',', ': '))
    with open('config.json', 'w') as a_file:
        a_file.write(json_str)


def read_config():
    try:
        a_file = open('config.json', 'r')
    except IOError as e:
        reset_config()
    else:
        a_file.close()
    with open('config.json', 'r') as a_file:
        json_dict = json.load(a_file)
    return (json_dict['API key'], json_dict['Steam ID'])


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


def makePlot(db):
    app_name = read_appnames_file()
    app_ids = db.app_ids_from_db()
    app_list = []
    for app_id in app_ids:
        app = App(app_id, app_name[str(app_id)])
        app.get_db_playtime(db.cursor)
        if max(app.last_day[-14:]) == 0:
            continue  # purge unplayed games
        app.last_day = app.last_day[-14:]
        for i in xrange(14 - len(app.last_day)):
            app.last_day.insert(0, 0)  # prepend empty slots with `0`
        app_list.append(app)
    x_all = []
    y_name = []
    today = int(time.time())
    for app in app_list:
        x_all.append(app.last_day)
        y_name.append(app.name)
    plot.plot_2weeks(today, x_all, y_name, options.filename)


def makeParser():
    parser = argparse.ArgumentParser(prog='steamplog', add_help=False)
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
            '--plot', dest='plot', action='store_true',
            help='plot playtime data for last 2 weeks')
    parser.add_argument(
            '-f', dest='filename',
            help='FILENAME of the plotted image')
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
    sys.exit(main())
