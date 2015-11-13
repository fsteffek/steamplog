#!/usr/bin/env python
"""steamplog - log and plot your steam gaming time

usage:
  steamplog.py log [<DATE>]
  steamplog.py plot [<DATE_FROM> [<DATE_TO>]]
                    [-lc] [-o FILE] [-v]
  steamplog.py stats [--full]

plot options:
  [<DATE_FROM>]     include every playtime from this date (format: YYYY-MM-DD)
                    [default: last 14 days]
  [<DATE_TO>]       include every playtime from this date (format: YYYY-MM-DD)
                    [default: today]
  -c, --color       top 10 games have different colors
  -l, --legend      include a legend
  -o FILENAME, --output FILENAME
                    FILENAME of the output image without extension

stats options:
  --full            print every game
other:
  -v, --verbose  be verbose
  -h, --help     show this help

"""

from __future__ import print_function
import sys
from datetime import datetime
from docopt import docopt

from steamplog.config import Config
from steamplog.downloader import Downloader
from steamplog.gamemgr import GameManager
from steamplog.plot import plot


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

    # Create GameManager
    GM = GameManager(config.Steam_ID)

    # Download the newest data
    if options['log'] or options['stats']:
        dl = Downloader(config.API_key)
        games = dl.download_stats(config.Steam_ID)

        GM.games = GM.prepare(games)

    # Stats
    if options['stats']:
        print('Current stats')
        for game in GM.games:
            print(game[1], '\t', GM.retrieve_appname(game[0]))
        sys.exit(0)

    # Log
    if options['log']:
        # Choose date to log
        if options['<DATE>'] is None:
            n = datetime.utcnow()
            unix_timestamp = int((n - datetime(1970, 1, 1)).total_seconds())
        else:
            n = parse_date(options['<DATE>'])
            unix_timestamp = int((datetime(n.year, n.month, n.day, 23, 59) -
                                  datetime(1970, 1, 1)).total_seconds())
        GM.log(unix_timestamp)
        sys.exit(0)

    # Plot
    if options['plot']:
        if options['<DATE_TO>'] is None:
            n = datetime.utcnow()
        else:
            n = parse_date(options['<DATE_TO>'])
        unix_to = int((datetime(n.year, n.month, n.day, 23, 59) -
                       datetime(1970, 1, 1)).total_seconds())
        if options['<DATE_FROM>'] is None:
            unix_from = unix_to - 1210000  # 14 days in seconds
        else:
            n = parse_date(options['<DATE_FROM>'])
            unix_from = int((datetime(n.year, n.month, n.day, 23, 59) -
                            datetime(1970, 1, 1)).total_seconds())
        # Get data
        GM.retrieve_log(unix_from, unix_to)
        # Sort
        GM.sort_most_played()
        make_plot(GM, unix_from, unix_to, config.tz)


def parse_date(date):
    return datetime.strptime(date, "%Y-%m-%d")


def make_plot(GM, unix_from, unix_to, tz):
    import copy
    import pytz
    # Set x-limits
    xlim = (datetime.utcfromtimestamp(unix_from),
            datetime.utcfromtimestamp(unix_to))

    if options['--color']:
        data = []
        offset = {}
        # Combine all minutes
        for app in GM.applist:
            one_data = []  # What is this?
            for d, m in zip(app.log_date, app.playtime):
                if d not in offset:
                    offset[d] = 0
                utc = datetime.utcfromtimestamp(d)
                utc = utc.replace(tzinfo=pytz.utc)
                one_data.append((utc.astimezone(pytz.timezone(tz)),
                                m, offset[d]))
                offset[d] = int(offset[d] + m)
            data.append(copy.copy(one_data))  # why use copy?
            one_data[:] = []
        # Set legend
        if options['--legend']:
            legend = [app.name[:25] for app in GM.applist[:10]] + ['Other']
        else:
            legend = None
        # Set filename
        if options['--output'] is None:
            options['--output'] = 'plot_detailed'
        plot(data, xlim=xlim, fname=options['--output'], plot_type='bar',
             legend=legend, title='Steamplog ('+options['--output']+')')
        print('\'' + options['--output'] + '.png\'')


if __name__ == "__main__":
    sys.exit(main())
