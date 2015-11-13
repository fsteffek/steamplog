from steamplog.database import SQLiteDB
from steamplog.downloader import Downloader


class GameManager(object):
    def __init__(self, steam_id):
        self.db = SQLiteDB('steamplog.db')
        self.db.setup_tables()
        self.dl = Downloader(None)
        self.games = []  # used for live game data
        self.applist = []

    def prepare(self, apps):
        '''
        Convert to sorted tuple and throw away zero minutes
        '''
        applist = [(x['appid'], x['playtime_forever']) for x in apps
                   if x['playtime_forever'] is not 0]
        return sorted(applist, key=lambda app: app[1], reverse=True)

    def log(self, unix_timestamp):
        '''
        Insert playtime data into db
        '''
        self.db.log_playtime(self.games, unix_timestamp)

    def update_appnames(self, applist):
        '''
        Keep app titles up2date
        '''
        print('This might take a while...')
        self.db.update_appnames_table(applist)

    def retrieve_appname(self, app_id):
        '''
        Retrieve 1 title of game with app_id
        '''
        name = self.db.retrieve_app_name(app_id)
        if name is []:
            self.update_appnames(self.dl.download_applist())
            name = self.db.retrieve_app_name(app_id)
        return name

    def retrieve_log(self, unix_from, unix_to):
        '''
        Calculate playtime for each day in timeframe
        '''
        for game in self.db.select_apps(unix_from, unix_to):
            app = App()
            app.app_id = game
            app.name = self.retrieve_appname(app.app_id)
            previous_day = 0
            for row in self.db.select_minutes(game, unix_from, unix_to):
                if previous_day == 0:
                    previous_day = row[1]
                    continue
                app.playtime.append(row[1] - previous_day)
                app.log_date.append(row[0])  # 24 hours
                previous_day = row[1]
            if app.playtime != []:
                self.applist.append(app)

    def sort_most_played(self):
        self.applist.sort(key=lambda app: max(app.playtime), reverse=True)


class App(object):
    def __init__(self):
        self.app_id = None
        self.name = None
        self.playtime = []
        self.log_date = []
