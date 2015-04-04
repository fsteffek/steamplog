#!/usr/bin/python
"""steamplog - log and plot your steam gaming time

usage:
  steamplog.py log
  steamplog.py plot [bar | point | line] [-a | [<DATE_FROM>] [<DATE_TO>]]
                    [-lc] [-o FILE | -i] [-v]
  steamplog.py update-appnames

plot options:
  -a, --all         plot every available playtime
  [<DATE_FROM>]     include every playtime from this date (format: YYYY-MM-DD)
                    [default: last 14 days]
  [<DATE_TO>]       include every playtime from this date (format: YYYY-MM-DD)
                    [default: today]
  -c, --color       top 5 games have different colors
  -l, --legend      include a legend
  -o FILENAME, --output FILENAME
                    FILENAME of the output image without extension
  -i, --individual  plot each game in a new image

other:
  -v, --verbose  be verbose
  -h, --help     show this help

"""

import sys
import json
import time
import datetime

from steamplog.app import App
from steamplog.db import steamplog_db
import steamplog.plot as plot
import steamplog.utils as utils
from docopt import docopt


def main(argv=None):
    if argv is None:
        argv = sys.argv
    global options
    global application_name
    options = docopt(__doc__, argv=argv[1:])
    print options
    #sys.exit(0)
    application_name = argv[0]
    #parser = makeParser()
    #options = parser.parse_args(argv[1:])
    #if options.reset_config:
    #    reset_config()
    #    sys.exit(0)

    (api_key, steam_id, db_host) = read_config()

    db = steamplog_db(db_host)

    db.configure()

    if options['update-appnames']:
        db.update_appnames(utils.get_app_list())
        db.close()
        sys.exit(0)

    if options['plot']:
        #db.migrate()
        print 'Plotting'
        makePlot2(db)
        db.close()
        sys.exit(0)

    owned_games = utils.get_owned_games(api_key, steam_id)

    if 'games' not in owned_games:
        print >> sys.stderr, application_name + ': ERROR: No games found'
        db.close()
        sys.exit(0)

    #if options.pretty_print:
    #    print json.dumps(owned_games, indent=4, separators=(',', ': '))
    #    sys.exit(0)
    #if options.print_only:
    #    print owned_games
    #    sys.exit(0)

    if options['log']:
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
    plot.plot_2weeks(today, x_all, y_name, options['-f'])

def parse_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")

def makePlot2(db):
    import copy
    if options['<DATE_TO>'] == None:
        dt_to = datetime.datetime.now()
    else:
        dt_to = parse_date(options['<DATE_TO>'])
    if options['<DATE_FROM>'] == None:
        dt_from = dt_to - datetime.timedelta(days=14)
    else:
        dt_from = parse_date(options['<DATE_FROM>'])
    if options['--all']:
        dt_to = datetime.datetime.now()
        dt_from = datetime.datetime(2014, 6, 10)
    plot_type = 'bar'
    if options['point']:
        plot_type = 'point'
    if options['line']:
        plot_type = 'line'
    xlim = (dt_from, dt_to)  # TODO: add commandline switch
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
    if options['--color']:  # different color apps
        data = []
        offset = {}
        # Combine all minutes off all apps
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
        if options['--legend']:
            legend = [app.name for app in app_list[:5]] + ['Other']
        else:
            legend = None
        if options['--output'] is None:
            options['--output'] = 'plot_detailed'
        plot.plot(data, xlim=xlim, fname=options['--output'], plot_type='bar',
                  legend=legend,
                  title='Steamplog (detailed)')
        print '\'' + options['--output'] + '.png\''
    elif options['--individual']:
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
            plot.plot(data, xlim=xlim, fname='plots/'+app.name,
                      plot_type=plot_type, title=app.name)
            print '\'plots/' + app.name + '.png\''
            app_data.clear()
            data[:] = []
    else: # plot all in one plot
        if options['--output'] is None:
            options['--output'] = 'plot_all'
        data = merge_playtimes(app_list)
        plot.plot(data, xlim=xlim, fname=options['--output'], plot_type=plot_type,
                  title='Steamplog')
        print '\'' + options['--output'] + '.png\''

def merge_playtimes(app_list):
    playtime = {}
    for app in app_list:
        for d, m in zip(app.date, app.last_day):
            playtime[d] = playtime[d] + m if d in playtime else m
    return [(datetime.datetime.utcfromtimestamp(d),
             playtime[d]) for d in playtime]


if __name__ == "__main__":
    sys.exit(main())
