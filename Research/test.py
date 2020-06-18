import requests

url = 'https://www.supremenewyork.com/shop/jackets/eq90f43yk/uwlas89kv'
url = 'https://www.supremenewyork.com/shop/new'
url = 'https://www.supremenewyork.com/shop/bags/wl7y6kc18/lr129h7zs'

with open("myfile.html", "w") as file:
	file.write(requests.get(url).text)