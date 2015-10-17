SteamPlog
=============

![Steamplog Q1-2015](https://photos-5.dropbox.com/t/2/AAAPogR-i9_c0QAt3mo0fWJZP7XAu0Md-blUTC8f6S67hQ/12/30030600/png/32x32/1/1445097600/0/2/4_56662202161037332.png/CIj2qA4gASACIAMgBSAHKAEoAigH/DX2qWn4daAbcSErhP6814FFP3pkuwpcP-GMFZ4yJXik?size=1024x768&size_mode=2)

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

