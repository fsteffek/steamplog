steamplaytime
=============

This script saves your game playtime for your steam games.

Note: steamplaytime is not endorsed, sponsored, affiliated with or otherwise authorized by Valve Corporation.

### Setup

#### Requirements
* [Steam API Key](http://steamcommunity.com/dev) ([Powered by Steam](http://steampowered.com))
* Python 2.7.6+ (lower versions untested)
* MySQL Server
* MySQLdb for Python (`python-mysqldb`)

#### MySQL Server
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

### Download
```bash
$ git clone https://github.com/fsteffek/steamplaytime.git
```
A softlink makes it more accessible.
```bash
$ cd steamplaytime
$ sudo ln -s steamplaytime.py /usr/local/bin/steamplaytime
```
Add your API Key and your Steam ID to `SteamPlaytimeSecret.py`.

### Automating
To automatically run this script every day at 5 in the morning, edit your cronfile.
```bash
$ crontab -e
```
Insert the following line at the end.
```
0 5 * * * /usr/local/bin/steamplaytime
```

