from flask import Flask, render_template
from datetime import datetime
import json, html, os

app = Flask(__name__)

@app.route('/')
def index():
	subs = []
	for a in os.listdir('r/'):
		if os.path.isdir('r/{}'.format(a)):
			subs.append('<div class="postinfo"><a href="/r/{}">{}</a></div><br>\n'.format(a, a))
	return render_template('subs_page.html', subs=''.join(subs))

@app.route('/r/<sub>')
def subreddit(sub):
	for a in os.listdir('r/{}'.format(sub)):
		if os.path.isfile('r/{}/{}'.format(sub, a)):
			dates = []
			date = os.path.splitext('r/{}/{}'.format(sub, a))[0].split('/')[-1]
			dates.append('<div class="postinfo"><a href="{}">{}</a></div>\n'.format('/r/{}/date/{}'.format(sub, date), date))
			return render_template('sub_dates_list.html', sub=sub, dates=''.join(dates))

@app.route('/r/<sub>/date/<date>')
def sub_date(sub, date):
	json_file = open('r/{}/{}.json'.format(sub, date), 'r').read()
	loaded_json = json.loads(json_file)
	posts = []

	for a in loaded_json['data']['children']:
		if a['data']['is_self']:
			title = a['data']['title']
			author = a['data']['author']
			score = a['data']['score']
			date = datetime.fromtimestamp(a['data']['created_utc'])
			link = '/r/{}/post/{}'.format(sub, a['data']['id'])
			posts.append('''<div class="postinfo">[author: {}] [score: {}] [date: {}]<br>
<a href="{}">{}</a></div><br><br>\n'''.format(author, score, date, link, title))
	return render_template('sub_date.html', sub=sub, date=date, posts=''.join(posts))

@app.route('/r/<sub>/post/<id>')
def thread(sub, id):
	json_file = open('r/{}/posts/{}.json'.format(sub, id), 'r').read()
	loaded_json = json.loads(json_file)

	title = loaded_json[0]['data']['children'][0]['data']['title']
	post_body = loaded_json[0]['data']['children'][0]['data']['selftext_html']
	if post_body is None:
		post_body = title

	comments = loaded_json[1]['data']['children']
	comments_list = []
	for a in comments:
		try:
			comment_html = html.unescape(a['data']['body_html'])
			comment_author = a['data']['author']
			comment_score = a['data']['score']
			# print(comment_html)
			comments_list.append('|author: {}| |Score: {}|<div class="acomment"><p>'.format(comment_author, comment_score)+comment_html+'</p></div><br><br>')
		except KeyError:
			print('KeyError')
			pass


	return render_template('post_template.html', title=title, post_title=title, post_body=html.unescape(post_body), comments='\n'.join(comments_list))


if __name__ == "__main__":
	app.run()