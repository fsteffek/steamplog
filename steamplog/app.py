class App(object):
    def __init__(self, ID, name):
        self.ID = ID
        self.name = name
        self.date = []
        self.minutes = []
        self.last_day = []

    def id_str(self):
        return str(self.ID)

    def get_db_playtime(self, cursor):
        query = 'SELECT time_of_record, minutes_played, appid FROM ' \
                + 'playtime_forever WHERE appid=\'' + self.id_str() \
                + '\' ORDER BY time_of_record'
        cursor.execute(query)
        previous = 0
        for row in cursor:
            self.date.append(row[0])
            if not self.minutes:
                self.last_day.append(0L)
            else:
                self.last_day.append(row[1] - previous)
            previous = row[1]
            self.minutes.append(row[1])
