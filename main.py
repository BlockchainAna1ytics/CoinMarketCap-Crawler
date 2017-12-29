import os
import itertools
import requests
import json
import time
from bs4 import BeautifulSoup

COIN_GRAPH_COUNT = 100
SAVE_FOLDER = "../coin-data/"
SLEEP_TIME_BETWEEN_REQUESTS = 2

class cspider:#static class
	def create_folder(folder_name):
		os.makedirs(folder_name)

	def is_folder_exist(folder_name):
		return os.path.exists(folder_name) and os.path.isdir(folder_name)

	def save_data_to_file(data,folder_name,file_name):
		if(folder_name[len(folder_name)-1] != '/' and file_name[0] != '/'):
			folder_name += '/'
		if(not cspider.is_folder_exist(folder_name)):
			cspider.create_folder(folder_name)
		save_path = folder_name+file_name
		file_write = open(save_path,"w")
		print(data,file=file_write)
		file_write.close()
	
	def get_page(url):
		print("Getting : "+url)
		try:
			req = requests.get(url)
			req.raise_for_status()
		except requests.exceptions.HTTPError as e:
			if(req.headers['Retry-After']):#sometimes this returns Date i should control it too
				exit("Banned, Try Again After " + str( int(int(req.headers['Retry-After'])/60) ) + " Minutes")
			else :
				exit(e)
		return req
	
	def get_coin_graph(coin_url):
		URL = "https://graphs.coinmarketcap.com"+coin_url
		page = cspider.get_page(URL)
		json_data = json.loads(page.text)
		return json_data['price_usd']

	def get_all_coins():
		URL = "https://coinmarketcap.com/all/views/all/"
		page = cspider.get_page(URL)
		soup = BeautifulSoup(page.text,"html.parser")
		table = soup.find('tbody')
		coins = []
		for tr in table.find_all('tr'):
			coin = {}
			coin_name_holder = tr.find('a',class_='currency-name-container') 
			coin['url'] = coin_name_holder.get('href')
			coin['name'] = coin_name_holder.text.strip()
			coin['symbol'] = tr.find('span',class_='currency-symbol').text.strip()
			coin['market-cap'] = tr.find('td',class_='market-cap').get('data-usd')
			coin['price'] = tr.find('a',class_='price').get('data-usd')
			coin['volume'] = tr.find('a',class_='volume').get('data-usd')
			try :
				coin['supply'] = tr.find('td',class_='circulating-supply').find('a').get('data-supply')
			except : 
				coin['suuply'] = "None"
			try :
				coin['change-24h'] = tr.find('td',class_='percent-24h').get('data-usd')
			except:
				coin['change-24h'] = "None"
			try :
				coin['change-1h'] = tr.find('td',class_='percent-1h').get('data-usd')
			except:
				coin['change-1h'] = "None"
			try :
				coin['change-7d'] = tr.find('td',class_='percent-7d').get('data-usd')
			except:
				coin['change-7d'] = "None"	
			coins.append(coin)
		return coins

	def run():
		coins = cspider.get_all_coins()[0:COIN_GRAPH_COUNT]
		json_coins = json.dumps(coins,indent=4)
		for coin in coins:
			coin['graph'] = cspider.get_coin_graph(coin['url'])
			time.sleep(SLEEP_TIME_BETWEEN_REQUESTS)
		cspider.save_data_to_file(json_coins,SAVE_FOLDER,"coins")
		print("All Coins Saved")

cspider.run();