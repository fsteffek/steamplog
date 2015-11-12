#!/usr/bin/env python
"""steamplog - log and plot your steam gaming time

usage:
  steamplog.py log
  steamplog.py plot [bar | point | line] [-a | [<DATE_FROM>] [<DATE_TO>]]
                    [-lc] [-o FILE | -i] [-v]
  steamplog.py update-appnames
  steamplog.py stats [--full]

plot options:
  -a, --all         plot every available playtime
  [<DATE_FROM>]     include every playtime from this date (format: YYYY-MM-DD)
                    [default: last 14 days]
  [<DATE_TO>]       include every playtime from this date (format: YYYY-MM-DD)
                    [default: today]
  -c, --color       top 10 games have different colors
  -l, --legend      include a legend
  -o FILENAME, --output FILENAME
                    FILENAME of the output image without extension
  -i, --individual  plot each game in a new image

stats options:
  --full            print every game

other:
  -v, --verbose  be verbose
  -h, --help     show this help

"""

from __future__ import print_function
import sys
import json
import time
import datetime
from docopt import docopt


from steamplog.config import Config
from steamplog.gamemgr import AppMGR, App
import steamplog.plot as plot
import steamplog.utils as utils


def main(argv=None):
    if argv is None:
        argv = sys.argv
    global options
    global application_name
    options = docopt(__doc__, argv=argv[1:])
    application_name = argv[0]

    # Load API Key and Steam UserID
    config = Config()
    config.load()

    AM = AppMGR(config.DB_engine,
                date_limit=config.date_limit)

    if options['--verbose']:
        print('Engine:', config.DB_engine)
    AM.db.create_tables()

    if options['update-appnames']:
        print(application_name + \
                ': INFO: This might take a while', file=sys.stderr)
        AM.update_names()
        AM.db.close()
        sys.exit(0)

    if options['stats']:
        AM.get_max_minutes()
        total_sum = 0
        for app in AM.applist:
            total_sum = total_sum + app.playtime
        print('Steam total playtime:', "%0.2f" % (total_sum/60.0), 'hours', \
              "(%0.2f days)" % (total_sum/60.0/24.0))
        print('')
        if options['--full']:
            for game in AM.applist:
                print("%0.2f" % (game.playtime/60.0), 'hours','\t', game.name)
        else:
            for game in AM.applist[:10]:
                print("%0.2f" % (game.playtime/60.0), 'hours','\t', game.name)
        sys.exit(0);

    if options['plot']:
        # Set options
        if options['<DATE_TO>'] == None:
            AM.set_to(utils.datetime2unix(datetime.datetime.now()))
        else:
            AM.set_to(utils.datetime2unix(parse_date(options['<DATE_TO>'])))
        if options['<DATE_FROM>'] == None:
            AM.set_from(AM.get_to() - 1209600)
        else:
            AM.set_from(utils.datetime2unix(
                parse_date(options['<DATE_FROM>'])))
        # Set date to all available logs
        if options['--all']:
            AM.set_to(utils.datetime2unix(datetime.datetime.now()))
            AM.set_from(utils.datetime2unix(datetime.datetime(2014, 6, 1)))

        if options['--verbose']:
            print('Plotting...')
        AM.games_played = AM.find_games_played()
        AM.process_games_played()
        AM.sort_most_played()
        makePlot(AM)
        AM.db.close()
        sys.exit(0)

    owned_games = utils.get_owned_games(config.API_key, config.Steam_ID)

    if 'games' not in owned_games:
        print(application_name + ': ERROR: No games found', file=sys.stderr)
        AM.db.close()
        sys.exit(0)

    if options['log']:
        data = [(x['appid'], x['playtime_forever']) for x in
                owned_games['games']]
        now = utils.round_datetime(datetime.datetime.utcnow())
        AM.db.log_playtime(data, utils.datetime2unix(now))
        time.sleep(10)

    # Disconnect from database
    AM.db.close()


def parse_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def makePlot(AM):
    import copy
    # Set plot type
    plot_type = 'bar'
    if options['point']:
        plot_type = 'point'
    if options['line']:
        plot_type = 'line'
    # Set x-limits
    xlim = (AM.get_dt_from(), AM.get_dt_to())

    if not AM.applist:
        info = application_name + ': INFO: No data found between ' + \
            AM.get_dt_from().strftime("%Y-%m-%d") + ' and ' + \
            AM.get_dt_to().strftime("%Y-%m-%d")
        print(info, file=sys.stderr)
        sys.exit(0)

    # 3 different plotting options
    if options['--color']:  # different color apps
        data = []
        offset = {}
        # Combine all minutes off all apps
        for app in AM.applist:
            one_data = []
            for d, m in zip(app.date, app.playtime):
                if d not in offset:
                    offset[d] = 0
                one_data.append((datetime.datetime.utcfromtimestamp(d),
                                 m, offset[d]))
                offset[d] = int(offset[d] + m)
            data.append(copy.copy(one_data))
            one_data[:] = []
        if options['--legend']:
            legend = [app.name[:25] for app in AM.applist[:10]] + ['Other']
        else:
            legend = None
        if options['--output'] is None:
            options['--output'] = 'plot_detailed'
        plot.plot(data, xlim=xlim, fname=options['--output'], plot_type='bar',
                  legend=legend,
                  title='Steamplog ('+options['--output']+')')
        print('\'' + options['--output'] + '.png\'')
    elif options['--individual']:
        for app in AM.applist:
            app_data = {}
            for date, minutes in zip(app.date, app.playtime):
                if date in app_data:
                    app_data[date] = app_data[date] + minutes
                else:
                    app_data[date] = minutes

            data = [(datetime.datetime.utcfromtimestamp(key),
                     app_data[key]) for key in app_data]
            data.sort()
            plot.plot(data, xlim=xlim, fname='plots/'+app.name,
                      plot_type=plot_type, title=app.name)
            print('\'plots/' + app.name + '.png\'')
            app_data.clear()
            data[:] = []
    else:  # plot all in one plot
        if options['--output'] is None:
            options['--output'] = 'plot_all'
        data = merge_playtimes(AM.applist)
        plot.plot(data, xlim=xlim, fname=options['--output'],
                  plot_type=plot_type, title='Steamplog')
        print('\'' + options['--output'] + '.png\'')


def merge_playtimes(app_list):
    playtime = {}
    for app in app_list:
        for d, m in zip(app.date, app.playtime):
            playtime[d] = playtime[d] + m if d in playtime else m
    return [(utils.unix2datetime(d), playtime[d]) for d in playtime]


if __name__ == "__main__":
    sys.exit(main())
