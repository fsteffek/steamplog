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
        sys.exit(0)
    if not options.filename:
        options.filename = 'output.png'

    (api_key, steam_id, db_host) = read_config()

    db = steamplog_db(db_host)

    db.configure()

    if options.update_appnames:
        db.update_appnames(utils.get_app_list())
        sys.exit(0)

    if options.plot:
        if options.plot_type is None:
            options.plot_type = 'bar'
        #db.migrate()
        print 'Plotting'
        makePlot2(db)
        sys.exit(0)

    owned_games = utils.get_owned_games(api_key, steam_id)

    if 'games' not in owned_games:
        print >> sys.stderr, application_name + ': ERROR: No games found'
        sys.exit(0)

    if options.pretty_print:
        print json.dumps(owned_games, indent=4, separators=(',', ': '))
        sys.exit(0)
    if options.print_only:
        print owned_games
        sys.exit(0)

    if options.save:
        data = [(x['appid'], x['playtime_forever']) for x in
                owned_games['games']]
        now = utils.round_datetime(datetime.datetime.utcnow())
        db.log_playtime_new(data, now)
        #db.log_playtime(owned_games)
        time.sleep(10)

    # Disconnect from database
    db.close()


def reset_config():
    json_str = json.dumps(
            {'API key': 'YourKey',
             'Steam ID': 'YourID',
             'MySQL host': 'localhost'},
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
    config_tuple = (json_dict['API key'],
                    json_dict['Steam ID'],
                    json_dict['MySQL host'])
    return config_tuple


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

def parse_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")

def makePlot2(db):
    import copy
    if options.date_to:
        dt_to = parse_date(options.date_to)
    else:
        dt_to = datetime.datetime.now()
        dt_to = datetime.datetime(dt_to.year, dt_to.month, dt_to.day)
    if options.date_from:
        dt_from = parse_date(options.date_from)
    else:
        dt_from = dt_to - datetime.timedelta(days=14)
    if options.date_all:
        dt_to = datetime.datetime.now()
        dt_from = datetime.datetime(2014, 6, 10)
    apps_in_range = db.fetch_app_ids_range(dt_from, dt_to)
    app_list = []
    for application in apps_in_range:
        app_name = db.get_app_name(application[0])
        app = App(application[0], app_name[0][1])
        previous = 0
        for row in db.fetch_playtimes_range(application[0], dt_from, dt_to):
            app.date.append(row[1] - 86400)
            if not app.minutes:
                app.last_day.append(0L)
            else:
                app.last_day.append(row[2] - previous)
            previous = row[2]
            app.minutes.append(row[2])
        if max(app.last_day) == 0:
            continue
        app_list.append(app)
    # Sort apps by most played per day
    app_list.sort(key=lambda app: max(app.last_day), reverse=True)
    if not app_list:
        info = application_name + ': INFO: You have not played between ' + \
            dt_from.strftime("%Y-%m-%d") + ' and ' + \
            dt_to.strftime("%Y-%m-%d")
        print >> sys.stderr, info
        sys.exit(0)
    # 3 different plotting options
    # Combine all minutes off all apps
    if options.plot_detailed:  # different color apps
        data = []
        offset = {}
        for app in app_list:
            one_data = []
            for d, m in zip(app.date, app.last_day):
                if d not in offset:
                    offset[d] = 0
                one_data.append((datetime.datetime.utcfromtimestamp(d),
                                 m, offset[d]))
                offset[d] = int(offset[d] + m)
                #print offset
            data.append(copy.copy(one_data))
            one_data[:] = []
        if options.plot_legend:
            legend = [app.name for app in app_list[:5]] + ['Other']
        else:
            legend = None
        plot.plot(data, fname='plot_detailed', plot_type='bar',
                  legend=legend,
                  title='Steamplog (detailed)')
        print '\'plot_detailed.png\''
    elif options.plot_separate:
        for app in app_list:
            app_data = {}
            for date, minutes in zip(app.date, app.last_day):
                if date in app_data:
                    app_data[date] = app_data[date] + minutes
                else:
                    app_data[date] = minutes

            data = [(datetime.datetime.utcfromtimestamp(key),
                     app_data[key]) for key in app_data]
            data.sort()
            plot.plot(data, fname='plots/'+app.name,
                      plot_type=options.plot_type, title=app.name)
            print '\'plots/'+app.name+'.png\''
            app_data.clear()
            data[:] = []
    else: # plot all in one plot
        data = merge_playtimes(app_list)
        plot.plot(data, fname='plot_all', plot_type=options.plot_type,
                  title='Steamplog')
        print '\'plot_all.png\''

def merge_playtimes(app_list):
    playtime = {}
    for app in app_list:
        for d, m in zip(app.date, app.last_day):
            playtime[d] = playtime[d] + m if d in playtime else m
    return [(datetime.datetime.utcfromtimestamp(d),
             playtime[d]) for d in playtime]


def makeParser():
    parser = argparse.ArgumentParser(prog='steamplog', add_help=False)
    # parser.add_argument(
    #         '-n', '--dry-run', dest='dry_run', action='store_true',
    #         help='do not connect to steam server')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
            '-p', '--print-only', dest='print_only', action='store_true',
            help='print current playtime data and exit')
    group1.add_argument(
            '-P', '--pretty-print', dest='pretty_print', action='store_true',
            help='like -p but print it in a human-readable format')
    group1.add_argument(
            '--reset-config', dest='reset_config', action='store_true',
            help='remove sensitive data from config.json')
    parser.add_argument(
            '--plot', dest='plot', action='store_true',
            help='plot playtime data for last 2 weeks')
    parser.add_argument(
            '-f', dest='filename',
            help='FILENAME of the plotted image')
    parser.add_argument(
            '--from', dest='date_from',
            help='datetime from in format Y-m-d (e.g. 2000-1-1)')
    parser.add_argument(
            '--to', dest='date_to',
            help='datetime to in format Y-m-d (e.g. 2000-1-1)')
    parser.add_argument(
            '--all', dest='date_all', action='store_true',
            help='print all available data')
    parser.add_argument(
            '--plot_type', dest='plot_type', choices=['bar','point','line'],
            help='plot as bar, point or line')

    group_content = parser.add_mutually_exclusive_group()
    group_content.add_argument(
            '--detailed', dest='plot_detailed', action='store_true',
            help='each game has its own color')
    group_content.add_argument(
            '--separate', dest='plot_separate', action='store_true',
            help='each game has its own plot')
    parser.add_argument(
            '--legend', dest='plot_legend', action='store_true',
            help='add legend to plot')
    group1.add_argument(
            '--save', dest='save', action='store_true',
            help='record new playtime into database')
    group1.add_argument(
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
