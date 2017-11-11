from datetime import datetime
import requests, json, sys, os, threading, time, re

sub = sys.argv[1]
date = datetime.now().strftime('%Y-%m-%d')
url = 'https://www.reddit.com/r/{}/top.json?sort=top&t=day&limit=20'.format(sub)
headers = {'User-Agent': 'Post Archiver'}
threads = []
extensions = ['.jpg', '.png', '.jpeg', '.gif', '.mp4', '.webm', '.gifv']
links = []
finished_links = []

os.makedirs('r/{}/posts'.format(sub), exist_ok=True)

list_json = requests.get(url, headers=headers).text
loaded_list_json = json.loads(list_json)
with open('r/{}/{}.json'.format(sub, date), 'w') as f:
	f.write(list_json)

def download(url, id):
	json_file = requests.get(url, headers=headers).text
	with open('r/{}/posts/{}.json'.format(sub, id), 'w') as f:
		f.write(json_file)
def download_image(url, file_name):
	print(file_name)
	with open('static/images/{}/{}'.format(sub, file_name), "wb") as file:
		response = requests.get(url, headers=headers)
		file.write(response.content)

for a in loaded_list_json['data']['children']:
	json_url = 'https://reddit.com'+a['data']['permalink']+'.json'
	thread_id = a['data']['id']

	t = threading.Thread(target=download, args=(json_url, thread_id,))
	t.start()
	threads.append(t)

	link = a['data']['url'], a['data']['id']
	if 'gfycat' in link[0] or 'imgur' in link[0] or 'i.redd.it' in link[0] or link[0].endswith(tuple(extensions)):
		os.makedirs('static/images/{}'.format(sub), exist_ok=True)
		links.append(link)
	time.sleep(0.2)

for c in links:
	if "imgur.com" in c[0]:
		if '/a/' in c[0] or '/gallery/' in c[0]:
			finished_links.append(c)

		elif c[0].endswith(tuple(extensions)):
			if c[0].endswith('.gifv'):
				newurl = c[0].replace(".gifv",".mp4")
				finished_links.append(tuple([newurl, c[1]]))

			else:
				finished_links.append(c)

		else:
			html_page = requests.get(c[0])
			if html_page.status_code == 404:
				print('404: skipping')
			else:
				print(c[0])
				imgur_id = c[0].split('/')[-1]
				try:
					link = re.findall('(?:href|src)="(?:https?:)?(\/\/i\.imgur\.com\/{}\.\S+?)"'.format(imgur_id), html_page.text)[0]
					link = 'https:' + link
					finished_links.append(tuple([link, c[1]]))
				except IndexError:
					print('IndexError on link {}'.format(c[0]))
					fixedlink = c[0].split('?')[0]
					print(fixedlink)
					pass

	elif "i.redd.it" in c[0] or "i.reddituploads.com" in c[0]:
		finished_links.append(c)

	elif "gfycat.com" in c[0] and not c[0].endswith('.webm'):
		gfycat_id = c[0].split('/')[-1]
		link = 'http://giant.gfycat.com/{}.webm'.format(gfycat_id)
		finished_links.append(tuple([link, c[1]]))

	elif c[0].endswith(tuple(extensions)):
		finished_links.append(c)

try:
	for d in finished_links:
		a_imgnumber = 0
		a_threads = []
		donelinks = []
		if '/a/' in d[0] or '/gallery/' in d[0]:
			os.makedirs('static/images/{}/{}'.format(sub, d[1]))
			html_page = requests.get(d[0] + '/layout/blog')
			if html_page.status_code == 404:
				print('404: skipping')
			else:
				imglinks = re.findall(r'\.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', html_page.text)
				for i in imglinks:
					try:
						if i[0]+i[1] not in donelinks:
							a_imgnumber += 1
							if i[1] == '.gif':
								ext = '.mp4'
							else:
								ext = i[1]
							g = threading.Thread(target=download_image, args=('https://i.imgur.com/'+i[0]+ext, '{}/{}'.format(d[1], str(a_imgnumber)+ext)))
							a_threads.append(g)
							g.start()
							donelinks.append(i[0]+i[1])
					except KeyboardInterrupt:
						print('\nCtrl-C Pressed; Finishing current threads then stopping...')
						for f in a_threads:
							f.join()
						sys.exit()
				for f in a_threads:
					f.join()
		else:
			ext = os.path.splitext(d[0])[1]
			t = threading.Thread(target=download_image, args=(d[0], d[1]+ext))
			t.start()
			threads.append(t)

	for e in threads:
		e.join()

except KeyboardInterrupt:
	print('\nCtrl-C Pressed; Finishing current threads then stopping...')
	for e in threads:
		e.join()
	sys.exit()


for b in threads:
	b.join()

print('All done!')