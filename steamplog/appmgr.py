from datetime import datetime
import steamplog.appdb as appdb
import steamplog.utils as utils


class AppMGR(object):
    def __init__(self, engine, host=None, date_limit=None):
        if engine == 'MySQL':
            self.db = appdb.MySQLDB('10.0.0.3')
            self.db_host = host
        elif engine == 'SQLite':
            self.db = appdb.SQLiteDB()
        self.applist = []
        self.games_played = []
        self.date_limit = None

    def set_from(self, timestamp):
        self.unix_timestamp_from = timestamp

    def get_from(self):
        return self.unix_timestamp_from

    def set_to(self, timestamp):
        self.unix_timestamp_to = timestamp

    def get_to(self):
        return self.unix_timestamp_to

    def get_dt_from(self):
        return utils.unix2datetime(self.unix_timestamp_from)

    def get_dt_to(self):
        return utils.unix2datetime(self.unix_timestamp_to)

    def update_names(self):
        applist = utils.download_applist()
        self.db.update_appnames_table(applist)

    def log(self, data, unix_timestamp):
        self.db.log_playtime(data, unix_timestamp)

    def sort_most_played(self):
        self.applist.sort(key=lambda app: max(app.playtime), reverse=True)

    def find_games_played(self):
        unix_from = self.get_from()
        unix_to = self.get_to()
        return self.db.select_apps(unix_from, unix_to)

    def process_games_played(self):
        '''Calculate playtime for each day and add it to list'''
        for game in self.games_played:
            app = App()
            app.app_id = game
            app.name = self.db.select_appnames(app.app_id)
            previous_day = 0
            for row in self.db.select_minutes(
                    app.app_id,
                    self.get_from(),
                    self.get_to()):
                if previous_day == 0:
                    previous_day = row[1]
                    continue
                app.playtime.append(row[1] - previous_day)
                app.date.append(row[0])  # 24 hours
                previous_day = row[1]
            if app.playtime != []:
                self.applist.append(app)


class App(object):
    def __init__(self):
        self.app_id = None
        self.name = None
        self.playtime = []
        self.date = []

    def set_appname(self, name):
        ''' Set the app's name'''
        self.name = name

    def get_appname(self):
        '''Returns the app's name'''
        return db.select_appnames(self.app_id)

    def exportCSV(self):
        '''TODO'''
        with open('exportCSV.txt', 'w') as a_file:
            for i in self.playtime:
                export_string = self.app_id + "\t" + self.name + "\n"
                a_file.write(export_string)
