from flask import Flask, render_template, url_for
from datetime import datetime
from natsort import natsorted
import json, html, os

app = Flask(__name__)
cwd = os.getcwd()

@app.route('/')
def index():
	subs = []
	for a in os.listdir('r/'):
		if os.path.isdir('r/{}'.format(a)):
			subs.append('<div class="postinfo"><a href="/r/{}">{}</a></div><br>\n'.format(a, a))
	return render_template('subs_page.html', subs=''.join(subs))

@app.route('/r/<sub>')
def subreddit(sub):
	dates = []
	for a in natsorted(os.listdir('r/{}'.format(sub))):
		pages = 0
		if os.path.isfile('r/{}/{}'.format(sub, a)) and 'r/{}/{}'.format(sub, a).endswith('_1.json'):
			for b in natsorted(os.listdir('r/{}'.format(sub))):
				if b.startswith(a.replace('_1.json','')):
					pages += 1
			date = os.path.splitext('r/{}/{}'.format(sub, a))[0].split('/')[-1].replace('_1','')
			dates.append('<div class="postinfo"><a href="{}/1">{}</a>({} pages)</div>\n<br>\n'.format('/r/{}/date/{}'.format(sub, date), date, str(pages)))
	return render_template('sub_dates_list.html', sub=sub, dates=''.join(dates))

@app.route('/r/<sub>/date/<date>/<page>')
def sub_date(sub, date, page):
	pages = 0
	for a in natsorted(os.listdir('r/{}/'.format(sub))):
		if a.endswith('.json') and a.startswith(date):
			pages += 1
	remaining_pages = pages - int(page)
	print(remaining_pages)
	json_file = open('r/{}/{}_{}.json'.format(sub, date, page), 'r').read()
	loaded_json = json.loads(json_file)
	posts = []

	for a in loaded_json['data']['children']:
		title = a['data']['title']
		author = a['data']['author']
		score = a['data']['score']
		date = datetime.fromtimestamp(a['data']['created_utc'])
		link = '/r/{}/post/{}'.format(sub, a['data']['id'])
		posts.append('''<div class="postinfo">[author: {}] [score: {}] [date: {}]<br>
<a href="{}">{}</a></div><br><br>\n'''.format(author, score, date, link, title))
	if remaining_pages > 0:
		posts.append('''<div class="next-button"><a href="{}">Next</a></div><br><br>'''.format(str(int(page)+1)))
	else:
		posts.append('''<div class="next-button">No more pages</div><br><br>'''.format(str(int(page)+1)))
	return render_template('sub_date.html', sub=sub, date=date, posts=''.join(posts))

@app.route('/r/<sub>/post/<id>')
def thread(sub, id):
	json_file = open('r/{}/posts/{}.json'.format(sub, id), 'r').read()
	loaded_json = json.loads(json_file)

	title = loaded_json[0]['data']['children'][0]['data']['title']
	post_body = loaded_json[0]['data']['children'][0]['data']['selftext_html']
	is_self = loaded_json[0]['data']['children'][0]['data']['is_self']
	if post_body is None:
		post_body = title

	if not is_self:
		post_body = ''
		# image = '<img src="'+url_for('/r/{}/posts/images/{}.jpg'.format(sub, id))+'>'
		images = []
		for a in os.listdir('static/images/{}/'.format(sub)):
			if id in a:
				if os.path.isdir('static/images/{}/{}'.format(sub, a)):
					for b in natsorted(os.listdir('static/images/{}/{}'.format(sub, a))):
						if b.endswith(tuple(['.jpg', '.png', '.gif', '.jpeg'])):
							images.append('<img src="/static/images/{}/{}/{}" height="45%" width="45%"><br>'.format(sub, a, b))
						elif b.endswith(tuple(['.mp4', '.webm'])):
							images.append('<video width="40%" height="40%" autoplay loop controls><source src="/static/images/{}/{}/{}" type="video/mp4"></video>'.format(sub, a, b))
				else:
					if a.endswith(tuple(['.jpg', '.png', '.gif', '.jpeg'])):
						images.append('<img src="/static/images/{}/{}" height="45%" width="45%">'.format(sub, a))
					elif a.endswith(tuple(['.mp4', '.webm'])):
						images.append('<video width="40%" height="40%" autoplay loop controls><source src="/static/images/{}/{}" type="video/mp4"></video>'.format(sub, a))

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

	if not is_self:
		return render_template('post_template.html', title=title, post_title=title, post_body=html.unescape(post_body), image='\n'.join(images), comments='\n'.join(comments_list))
	else:
		return render_template('post_template.html', title=title, post_title=title, post_body=html.unescape(post_body), comments='\n'.join(comments_list))

if __name__ == "__main__":
	app.run()