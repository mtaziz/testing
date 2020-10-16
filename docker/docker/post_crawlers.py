import requests

spiders_url = "http://localhost:6800/listspiders.json?project=rvp-crawlers"
r = requests.get(spiders_url)
if r.status_code == 200:
    spiders = r.json()['spiders']
else:
    print(r.status_code, "list not found")
    spiders = []
url = "http://localhost:6800/schedule.json"
data = {"project": "rvp-crawlers"}
for spider_name in spiders:
    data['spider'] = spider_name
    requests.post(url, data=data)
