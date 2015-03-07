from datetime import datetime as dt
from datetime import date, timedelta
import itertools

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_2weeks(today, minutes, labels, fname=None, color=None):
    plot_n_days(14, today, minutes, labels, fname, color)


def plot_n_days(ndays, today, minutes, labels, fname=None, color=None):
    X = np.arange(float(ndays))
    legend_ = labels
    day_dt = dt.fromtimestamp(today)
    monday = day_dt - timedelta(days=ndays)

    # Color
    if color is None:
        # green, blue, orange, violet, brown-red, pink, red, grey
        color_ = ['#008C48', '#185AA9', '#F47D23', '#662C91',
                  '#EE2E2F', '#A21D21', '#B43894', '#010202',
                  '#7AC36A', '#5A9BD4', '#FAA75B', '#9E67AB',
                  '#CE7058', '#D77FB4', '#F15A60', '#737373',
                  '#D9E4AA', '#B8D2EC', '#F3D1B0', '#D5B2D4',
                  '#F2AFAD', '#DDB9A9', '#EBC0DA', '#CCCCCC']
    else:
        color_ = color

    # Initialize figure, axis
    fig, ax = plt.subplots()

    fig.autofmt_xdate(rotation=45)
    # Display 2009 as 2009 not 9+2e3
    ax.get_xaxis().get_major_formatter().set_useOffset(False)

    # Bar type plot
    bottom_ = np.array([0 for i in xrange(len(X))])
    for Y, c in zip(minutes, itertools.cycle(color_)):
        ax.bar(left=X, height=Y, width=0.8, bottom=bottom_, color=c)
        bottom_ += Y

    # X axis
    ax.set_xticks(np.arange(0.0, float(ndays), 1.0))
    date_list = [day_dt - timedelta(days=x) for x in range(0, ndays)]
    ax.set_xticklabels([i.strftime('%m-%d') for i in reversed(date_list)])
    ax.set_xlabel('Day')

    # Y axis
    ax.set_ylabel('Time [minutes]')

    # Grid
    ax.minorticks_on()
    ax.set_axisbelow(True)
    ax.grid(b=True, which='major', axis='y', linestyle='-')
    ax.grid(b=True, which='minor', axis='y')

    # Legend
    lgd = ax.legend(legend_,
                    loc=2,
                    bbox_to_anchor=(1.05, 1.0),
                    borderaxespad=0)

    # Title
    title_ = 'Steam Plog ' + monday.strftime('%Y-%m-%d')
    title_ += ' - ' + day_dt.strftime('%Y-%m-%d')
    plt.title(title_)

    # Save/Display
    plt.savefig(fname, dpi=72, bbox_extra_artists=(lgd,), bbox_inches='tight')
