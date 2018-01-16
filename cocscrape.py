import requests
import bs4
import util

url = 'https://www.cityofchicago.org/city/en.html'

req = requests.get(url)

html = req.text.encode('iso-8859-1')

soup = bs4.BeautifulSoup(html, 'lxml')

print(soup)
