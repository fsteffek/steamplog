SteamPlog
=============

This script logs and plots your game playtime for your steam games.

Note: steamplog can be considered `pre-alpha`.

Note: steamplog is not endorsed, sponsored, affiliated with or otherwise authorized by Valve Corporation.

### Setup

#### Requirements
* [Steam API Key](http://steamcommunity.com/dev) ([Powered by Steam](http://steampowered.com))
* Python 2.7.6+ (lower versions untested)
* MySQL Server
* `python-mysqldb`
* `python-matplotlib` (for creating graphs)

#### MySQL Server
Note: The MySQL server will eventually be replaced by an SQLite file.

If you have your mysql server on your local machine, type:
```bash
$ mysql
```
and create a new database and user `steam`
```sql
CREATE DATABASE 'steam';
CREATE USER 'steam';
GRANT ALL PRIVILEGES ON steam.* TO 'steam';
```

Create this table:
```sql
CREATE TABLE steam.playtime_forever ( 
    appid INT NOT NULL,
    minutes_played INT,
    time_of_record INT );
```

### Usage

After cloning the repo you should run steamplog with option `--reset-config`.
This creates the file `config.json` where you should add your API key and Steam ID.

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

