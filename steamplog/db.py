import MySQLdb
import time
from datetime import datetime
import sys


import utils


class steamplog_db(object):
    def __init__(self):
        self.conn = MySQLdb.connect(
                host="localhost",
                user="steam",
                db="steam",
                charset="utf8")
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def configure(self):
        self.cursor.execute(
            'SELECT * FROM information_schema.tables '
            'WHERE table_name = "app_names" LIMIT 1'
        )
        if not self.cursor.fetchall():
            self.cursor.execute(
                'CREATE TABLE app_names ('
                'app_id int(11) NOT NULL, '
                'name text COLLATE utf8_unicode_ci, '
                'PRIMARY KEY (app_id)'
                ') DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
            )
        self.cursor.execute(
            'SELECT * FROM information_schema.tables '
            'WHERE table_name = "playtime" LIMIT 1'
        )
        if not self.cursor.fetchall():
            self.cursor.execute(
                'CREATE TABLE playtime ('
                'app_id int(11) NOT NULL, '
                'logged_at int(11) NOT NULL, '
                'minutes_played int(11) NOT NULL, '
                'PRIMARY KEY (app_id, logged_at)'
                ')'
            )

    def migrate(self):
        self.cursor.execute(
                'SELECT DISTINCT time_of_record '
                'FROM playtime_forever '
                'ORDER BY time_of_record'
            )
        result = [row[0] for row in self.cursor.fetchall()]
        total = float(len(result))
        for i, row in enumerate(result):
            utils.update_progress(float(i)/total)
            self.cursor.execute(
                'SELECT * FROM playtime_forever WHERE time_of_record=%s',
                (row,))
            data = [(x[0], x[1]) for x in self.cursor.fetchall()]
            now = utils.round_datetime(datetime.datetime.utcfromtimestamp(row))
            self.log_playtime_new(data, now)

    def update_appnames(self, app_list):
        self.cursor.executemany(
            'REPLACE INTO app_names'
            '(app_id, name)'
            'VALUES (%s, %s)', app_list
            )
        self.conn.commit()

    def log_playtime(self, owned_games):
        """Insert playtime data into database"""
        time_in_unix = int(time.time())  # timestamp for db
        table = 'playtime_forever'
        for game in owned_games['games']:
            query = 'INSERT INTO ' + table
            query += ' ( appid, minutes_played, time_of_record ) VALUES ( '
            query += '%d, ' % game.get('appid', 0)
            query += '%d, ' % game.get(table, 0)
            query += '%d )' % time_in_unix
            self.cursor.execute(query)
        self.conn.commit()

    def log_playtime_new(self, data, log_date):
        """Insert playtime data into database"""
        time_in_unix = int((log_date - datetime(1970, 1, 1)).total_seconds())
        table = 'playtime'
        for app_data in data:
            # Update current minutes_played
            self.cursor.execute(
                    'SELECT app_id, logged_at '
                    'FROM ' + table + ' '
                    'WHERE app_id=%s AND logged_at=%s',
                    (app_data[0], time_in_unix))
            if self.cursor.fetchall():
                self.cursor.execute(
                        'UPDATE ' + table + ' '
                        'SET minutes_played=%s '
                        'WHERE app_id=%s AND logged_at=%s',
                        (app_data[1], app_data[0], time_in_unix))
                continue
            # ... or insert new log
            self.cursor.execute(
                    'SELECT app_id, minutes_played, logged_at '
                    'FROM ' + table + ' '
                    'WHERE app_id=%s AND minutes_played=%s',
                    (app_data[0], app_data[1]))
            if not self.cursor.fetchall():
                self.cursor.execute(
                        'INSERT INTO ' + table + ' '
                        '(app_id, minutes_played, logged_at) '
                        'VALUES (%s, %s, %s)',
                        (app_data[0], app_data[1], time_in_unix))
        self.conn.commit()

    def app_ids_from_db(self):
        """Get the app id for each game in database and return as list"""
        query = 'SELECT DISTINCT appid FROM playtime_forever ORDER BY appid'
        self.cursor.execute(query)
        table = self.cursor.fetchall()  # returns a tuple of tuples
        return [row[0] for row in table]
