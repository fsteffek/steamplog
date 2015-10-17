SteamPlog
=============

![Steamplog Q1-2015](https://www.dropbox.com/s/3cbpumi078l6sie/4_56662202161037332.png)

This script logs and plots your game playtime for your steam games.

Note: steamplog is not endorsed, sponsored, affiliated with or otherwise authorized by Valve Corporation.

### Setup

#### Requirements
* [Steam API Key](http://steamcommunity.com/dev) ([Powered by Steam](http://steampowered.com))
* Python 2.7.6+ (lower versions untested)
* either `sqlite3` or `python-mysqldb`
* `python-matplotlib`

### Usage

After cloning this repo you should run `steamplog.py create-config`.
This creates the file `config.json`. This is where you should add your API key and Steam ID.

Run with option `-h` to see all available options.

### Automating
To automatically run this script every day at 5 in the morning, edit your cronfile.
```bash
$ crontab -e
```
Insert the following line at the end.
```
0 5 * * * {path-to-steamplog.py}/steamplog.py --save
```

