# Reddit-Archive-Host

Set of tools for downloading and locally hosting text-based reddit content.

## Usage
#### Downloading posts:

`python3 Post-Archiver.py [Subreddit] [Time] [Number of posts]`

`Subreddit` will just be the name of the subreddit you want to archive.

`Time` will be the time range you want to archive. It will be day, week, month, year, or all

`Number of posts`is pretty self explanatory; It's how many posts you want to archive. The maximum (due to reddit's json api limitations) is 1000

#### Hosting downloaded posts:

`python3 Flask-Host.py`

This will start an instance of flask so that you can browse your downloaded subreddits in your browser. Just navigate to the url that flask gives you in the commandline.

## Other
[What browsing looks like](https://giant.gfycat.com/AmazingWellmadeAiredale.webm)

Required modules are: requests, natsort and flask.

You can install them with `pip3 install -U -r requirements.txt`