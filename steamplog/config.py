import json


class Config(object):
    def __init__(self, path=None):
        if path is None:
            self.path = 'config.json'
        else:
            self.path = path
        self.API_key = None
        self.Steam_ID = None
        self.tz = 'UTC'

    def load(self):
        try:
            a_file = open(self.path, 'r')
        except IOError:
            self.reset()
        else:
            a_file.close()
        with open(self.path, 'r') as a_file:
            json_dict = json.load(a_file)
        self.API_key = json_dict['API key']
        self.Steam_ID = json_dict['Steam ID']
        self.tz = json_dict['Timezone']

    def reset(self):
        json_str = json.dumps(
            {'API key': 'YourKey',
             'Steam ID': 'YourID',
             'Timezone': 'UTC'},
            sort_keys=False, indent=4, separators=(',', ': '))
        with open(self.path, 'w') as a_file:
            a_file.write(json_str)
