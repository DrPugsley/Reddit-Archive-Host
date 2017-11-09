from datetime import datetime
import requests, json, sys, os, threading, time

sub = sys.argv[1]
date = datetime.now().strftime('%Y-%m-%d')
url = 'https://www.reddit.com/r/{}/top.json?sort=top&t=day&limit=50'.format(sub)
headers = {'User-Agent': 'Text Archiver'}
threads = []

os.makedirs('r/{}/posts'.format(sub), exist_ok=True)

list_json = requests.get(url, headers=headers).text
loaded_list_json = json.loads(list_json)
with open('r/{}/{}.json'.format(sub, date), 'w') as f:
	f.write(list_json)

def download(url, id):
	json_file = requests.get(url, headers=headers).text
	with open('r/{}/posts/{}.json'.format(sub, id), 'w') as f:
		f.write(json_file)

for a in loaded_list_json['data']['children']:
	if a['data']['is_self']:
		json_url = a['data']['url']+'.json'
		print(json_url)
		thread_id = json_url.split('/')[6]

		t = threading.Thread(target=download, args=(json_url, thread_id,))
		t.start()
		threads.append(t)
		time.sleep(0.2)

for b in threads:
	b.join()

print('All done!')