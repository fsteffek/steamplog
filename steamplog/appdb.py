import time
from datetime import datetime
import sys


import MySQLdb
import sqlite3
import steamplog.utils as utils


class MySQLDB(object):
    def __init__(self, host=''):
        self.conn = MySQLdb.connect(
                    host=host,
                    user="steam",
                    db="steam",
                    charset="utf8")
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    # misc. operations
    def create_tables(self):
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

    # playtime table
    def select_apps(self, unix_from, unix_to):  # returns distinct app_ids
        self.cursor.execute(
                'SELECT app_id, logged_at FROM playtime '
                'WHERE %s <= logged_at AND logged_at <= %s GROUP BY app_id',
                (unix_from, unix_to))
        result = self.cursor.fetchall()  # returns [(app_id, logged_at)]
        return [app[0] for app in result]

    def select_minutes(self, app_id, unix_from, unix_to):
        self.cursor.execute(
                'SELECT logged_at, MAX(minutes_played) as minutes_played '
                'FROM playtime '
                'WHERE app_id=%s AND logged_at < %s',
                (app_id, unix_from))
        result = self.cursor.fetchall()
        if result[0][0] == None:
            result = [(unix_from, 0)]
        else:
            result = [result[0]]

        # Get data in specified range
        self.cursor.execute(
                'SELECT logged_at, minutes_played '
                'FROM playtime '
                'WHERE app_id=%s AND %s < logged_at AND logged_at <= %s',
                (app_id, unix_from, unix_to))
        result.extend([(app[0], app[1]) for app in self.cursor.fetchall()])
        return result

    def log_playtime(self, data, log_date):
        """Insert playtime data into database"""
        # data == [(app_id, minutes_played)]
        # log_date == datetime.datetime
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

    # appnames table
    def update_appnames_table(self, app_list):
        self.cursor.executemany(
            'REPLACE INTO app_names'
            '(app_id, name)'
            'VALUES (%s, %s)', app_list
            )
        self.conn.commit()

    def select_appnames(self, app_id):
        self.cursor.execute(
                'SELECT app_id, name FROM app_names WHERE app_id = %s',
                (app_id))
        name = self.cursor.fetchall()
        return name[0][1]
##############################################################################


class SQLiteDB(object):
    def __init__(self):
        self.db = sqlite3.connect(
            'steamplog.db',
            )
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    # misc. operations:
    def create_tables(self):
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS playtime\n'
            '    (\n'
            '        app_id INTEGER NOT NULL,\n'
            '        logged_at INTEGER NOT NULL,\n'
            '        minutes_played INTEGER NOT NULL,\n'
            '        PRIMARY KEY (app_id, logged_at)\n'
            '    )\n'
            )
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS app_names\n'
            '    (\n'
            '        app_id INTEGER PRIMARY KEY,\n'
            '        name TEXT\n'
            '    )\n'
            )
        self.db.commit()

    def tidy(self):
        self.cursor.execute('DELETE FROM playtime WHERE app_id = 0')

    # playtime table
    def select_apps(self, unix_from, unix_to):
        self.cursor.execute(
                'SELECT app_id, logged_at FROM playtime '
                'WHERE (?) <= logged_at AND logged_at <= (?) GROUP BY app_id',
                (unix_from, unix_to))
        result = self.cursor.fetchall()
        return [app[0] for app in result]

    def select_minutes(self, app_id, unix_from, unix_to):
        self.cursor.execute(
                'SELECT logged_at, max(minutes_played) '
                'FROM playtime '
                'WHERE app_id=(?) AND logged_at < (?)',
                (app_id, unix_from))
        result = self.cursor.fetchall()
        if result[0][0] == None:
            result = [(unix_from-86400, 0)]
        else:
            result = [result[0]]

        # Get data in specified range
        self.cursor.execute(
                'SELECT logged_at, minutes_played '
                'FROM playtime '
                'WHERE app_id=(?) AND (?) < logged_at AND logged_at <= (?)',
                (app_id, unix_from, unix_to))
        result.extend([(app[0]-86400, app[1]) for app in self.cursor.fetchall()])
        return result

    def log_playtime(self, data, unix_timestamp):
        for app_data in data:
            # Update old minutes_played ...
            self.cursor.execute(
                    'SELECT app_id, logged_at '
                    'FROM playtime '
                    'WHERE app_id=(?) AND logged_at=(?)',
                    (app_data[0], unix_timestamp))
            if self.cursor.fetchall():
                self.cursor.execute(
                    'UPDATE playtime '
                    'SET minutes_played=(?) '
                    'WHERE app_id=(?) AND logged_at=(?)',
                    (app_data[1], app_data[0], unix_timestamp))
                continue
            # ... or insert new log
            self.cursor.execute(
                    'SELECT app_id, minutes_played, logged_at '
                    'FROM playtime '
                    'WHERE app_id=(?) AND minutes_played=(?)',
                    (app_data[0], app_data[1]))
            if not self.cursor.fetchall():
                self.cursor.execute(
                        'INSERT INTO playtime '
                        '(app_id, minutes_played, logged_at) '
                        'VALUES (?,?,?)',
                        (app_data[0], app_data[1], unix_timestamp))
            self.db.commit()

    def select_max_minutes(self):
        self.cursor.execute(
                'SELECT app_id '
                'FROM playtime '
                'GROUP BY app_id ORDER by minutes_played DESC')
        result = self.cursor.fetchall()
        app_list = ()
        for app_id in result:
            self.cursor.execute(
                    'SELECT app_id, MAX(minutes_played) '
                    'FROM playtime '
                    ' WHERE app_id = (?)', app_id)
            result = self.cursor.fetchall()
            app_list = app_list + ((result[0]),)
        return app_list

    # appnames table
    def update_appnames_table(self, applist):
        self.db.executemany(
            'REPLACE INTO app_names'
            '(app_id, name)'
            'VALUES (?, ?)', applist
            )
        self.db.commit()

    def select_appnames(self, app_id):
        self.cursor.execute(
                'SELECT app_id, name FROM app_names WHERE app_id = (?)',
                (app_id,))
        name = self.cursor.fetchall()
        if name == []:
            print 'something bad happened'
            print app_id
            return 'uh oh'
        else:
            return name[0][1]
