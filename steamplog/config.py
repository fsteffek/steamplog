import json


class Config(object):

    def __init__(self):
        self.path = None
        self.API_key = None
        self.Steam_ID = None
        self.SQL_host = None

    def create(self):
        json_str = json.dumps(
            {'API key': 'YourKey',
             'Steam ID': 'YourID',
             'DB engine': 'SQLite',
             'MySQL host': 'localhost',
             'Date limit': 'DD-MM-YYYY'},
            sort_keys=False, indent=4, separators=(',', ': '))
        with open(self.path, 'w') as a_file:
            a_file.write(json_str)

    def read(self, config_path):
        self.path = config_path
        try:
            a_file = open(self.path, 'r')
        except IOError as e:
            self.create()
        else:
            a_file.close()
        with open(self.path, 'r') as a_file:
            json_dict = json.load(a_file)
        self.API_key = json_dict['API key']
        self.Steam_ID = json_dict['Steam ID']
        self.DB_engine = json_dict['DB engine']
        self.SQL_host = json_dict['MySQL host']
        self.date_limit = json_dict['Date limit']
