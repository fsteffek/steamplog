from datetime import datetime as dt
from datetime import date, timedelta
import itertools

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.dates import date2num
from matplotlib.ticker import MultipleLocator


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


def plot(data, xlim=None, legend=None, plot_type='bar', width=800, height=450,
         title='Steamplog', fname=None):
    dpi = 96.  # <= here be dragons
    width = width / dpi  # turn pixels into some inch value
    height = height / dpi  # turn pixels into some inch value

    # Initialize figure, axes
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)

    # Font settings
    tick_font_size = 10.
    # Tick labels
    font0 = FontProperties()
    font0.set_size(tick_font_size)
    font0.set_family('monospace')
    # Axis labels
    font1 = FontProperties()
    font1.set_family('monospace')
    font1.set_size(tick_font_size*(10./8.))
    # Title
    font2 = FontProperties()
    font2.set_family('monospace')
    font2.set_size(tick_font_size*(12./8.))

    # Colors
    color_plot = '#66c0f4'  # blueish
    color_text = '#787878'  # some kind of grey
    color_bg = '#222222'
    ax.set_axis_bgcolor(color_bg)

    # Plot as bar, points or line
    if plot_type == 'bar':
        if type(data[0]) is list:
            color_ = ['#89adba', '#b4da45', '#b84d1f', '#57739d',
                      '#b7b395', '#c98d33']  # '#89adba', '#b7b395']
            if len(data) < len(color_):
                color_ = color_[:len(data)]
            for messung, color4plot in \
                    itertools.izip_longest(data, color_, fillvalue=color_[-1]):
                # stack data on top of each other
                ax.bar([x[0] for x in messung], [y[1] for y in messung],
                       bottom=[bottom[2] for bottom in messung],
                       color=color4plot, edgecolor='none')
        else:
            ax.bar([x[0] for x in data], [y[1] for y in data],
                   color=color_plot, edgecolor='none')
    elif plot_type == 'point':
        ax.plot([x[0] for x in data], [y[1] for y in data],
                'o', color=color_plot)
    elif plot_type == 'line':
        X = [x[0] for x in playtimes_with_zero(data)]
        Y = [y[1] for y in playtimes_with_zero(data)]
        ax.plot(X, Y, color=color_plot)

    # Set the limits (x-axis)
    if xlim:
        plt.xlim((date2num(xlim[0]), date2num(xlim[1])))
    # Show at least up to 60 minute (y-axis)
    if ax.get_ylim()[1] - ax.get_ylim()[0] < 60.0:
        plt.ylim((ax.get_ylim()[0], ax.get_ylim()[0] + 60.0))
    # Label every hour (y-axis)
    ax.yaxis.set_major_locator(MultipleLocator(60))

    # Rotate xlabels and format as date
    fig.autofmt_xdate(rotation=90)

    # Set up the Grid
    ax.minorticks_on()
    ax.grid(b=True, which='major', color='#353539', axis='y')
    ax.grid(b=True, which='major', color='#353539', axis='x', linestyle='-')
    ax.grid(b=True, which='minor', color='#353539', axis='x')
    ax.set_axisbelow(True)

    # Set axis lables
    ax.set_xlabel('Date', color=color_text, fontproperties=font1)
    ax.set_ylabel('Minutes played', color=color_text, fontproperties=font1)
    for label in ax.get_xticklabels():
        label.set_fontproperties(font0)
        label.set_color(color_text)
        label.set_horizontalalignment('left')
    for label in ax.get_yticklabels():
        label.set_fontproperties(font0)
        label.set_color(color_text)
    plt.tight_layout()  # Do not cut axis labels

    # Set title
    plt.title(title, fontproperties=font2, color=color_text)

    # Legend
    if legend is not None:
        lgd = ax.legend(legend, loc=2, bbox_to_anchor=(1.05, 1.0),
                        borderaxespad=0)
        [text.set_color(color_text) for text in lgd.get_texts()]
        lgd.get_frame().set_facecolor(color_bg)
        # Output the graph
        plt.savefig(fname + '.png', dpi=dpi, facecolor='#333333',
                    bbox_extra_artists=(lgd,),
                    bbox_inches='tight')  # dragons be tight
    else:
        # Output the graph 2
        plt.savefig(fname + '.png', dpi=dpi, facecolor='#333333',
                    bbox_inches='tight')
    plt.show()
    plt.close(fig)


def playtimes_with_zero(playtimes, interval=timedelta(days=1), fillvalue=0):
    for pt, pt_next in itertools.izip_longest(playtimes, playtimes[1:],
                                              fillvalue=playtimes[-1]):
        dt_from = pt[0]  # datetime of current playtime
        dt_to = pt_next[0]  # datetime of next playtime
        if dt_to - dt_from > interval:
            yield pt
            dt_from = dt_from + interval
            while dt_to - dt_from > timedelta(0):
                yield (dt_from, fillvalue)  # 0 minutes_played
                dt_from = dt_from + interval
        else:
            yield pt


def main():
    r = matplotlib.mlab.csv2rec('steam_playtime_2weeks.csv')

    data = []
    dates = {}
    for row in r:
        if row[0] in dates:
            dates[row[0]] = dates[row[0]] + row[1]
        else:
            dates[row[0]] = row[1]
    for key in dates:
        mins = int(dates[key])
        data.append((dt.utcfromtimestamp(key), mins))
    data.sort()
    data = data[280:]
    data = [data, data]
    app_list = data
    if type(data[0]) is list:
        offset = {}
        for app in app_list:
            for date, minutes in zip(app.date, app.last_day):
                date = app_data[0]
                offset[date] = offset[date] + app_data[1] if date in offset else 0
            
    print data.__class__
    for x in data:
        print x
        print type(x)
        print type(x) is list
    print 'bar'
    plot(data, fname='unittest_bar', plot_type='bar')
    #print 'point'
    #plot(data, fname='unittest_point', plot_type='point')
    #print 'line'
    #plot(data, fname='unittest_line', plot_type='line')

if __name__ == "__main__":
    main()
