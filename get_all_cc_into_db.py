
#-*- coding:utf-8 -*-
import requests
import cookielib
import json
from bs4 import BeautifulSoup
from time import sleep
import random
import csv

url='https://www.hoau.net/how/bse/showPriceTime.action'
url_query='https://www.hoau.net/how/bse/queryPriceTime.action'


requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    pass

headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        'Host': "www.hoau.net",
        'Pragma': "no-cache",
        'Referer': "https://www.hoau.net/how/bse/showPriceTime.action",
        'X-Requested-With': "XMLHttpRequest"
    }

requests.get(url,headers=headers)
requests.cookies.save()




###get all city_country

#get all provinces_code
url_pro='https://www.hoau.net/how/bse/queryNewProvinces.action'
r=requests.get(url_pro,headers=headers)

a=json.loads(r.text)
all_provinces=[]

for x in a['districts']:
	all_provinces.append(x['districtCode'])
print 'there are ',len(all_provinces),' provinces!'


#get city_code and name according to provinces,return a list[]
def get_allcity():
	all_city=[]
	for i in all_provinces:
		url_get='https://www.hoau.net/how/bse/queryNewCitys.action?districtCode='+i
		r=requests.get(url_get,headers=headers)
		districts=(json.loads((requests.get(url_get,headers=headers)).text))['districts'] #list
		for x in districts:
			all_city.append((x['districtCode'],x['districtName']))  # unicode list
	return all_city

all_city=get_allcity()
print 'there are ',len(all_city),' cities!'


def str_save(mystr,filename):
	with open(filename,'a') as fp:
		fp.write('%s\n'%mystr)



# get country list by city_code, return list[]
def city_get_country(city_code):
	countries=[]
	url_get='https://www.hoau.net/how/bse/queryNewCitys.action?districtCode='+city_code
	#r=requests.get(url_get,headers=headers)
	districts=(json.loads((requests.get(url_get,headers=headers)).text))['districts'] #list
	for x in districts:
		countries.append(x['districtName'])  # unicode list  #or short_name??
	return countries


#get all the city_country into a list
def get_city_country():
	city_country=[]
	for i in range(len(all_city)):
		country_list=city_get_country(all_city[i][0])
		
		#create new list from city[i][1],country_list
		for x in country_list:
			city_country.append((all_city[i][1],x))

		if (i%5==0):
			sleep(random.uniform(0.5,1))
	return city_country


city_country=get_city_country()
print 'there are'+str(len(city_country))+'city_country'
str_save(city_country,'city_country.txt')








###get all the combination of city_country_to_city_country  3000*3000  into a txt file
# (len(_all))=3000*3000
#_all=[]
def get_all_combination():
	_all=[]
	for x in city_country:
		for y in city_country:
			_all.append((x,y))
	return _all

_all=get_all_combination()
print 'we finished combination,there are ',len(_all),' combinations!'

def list_save(_all,filename):
	with open(filename,'w') as fp:
		for x in _all:
			fp.write(x[0][0].encode('utf-8'))
			fp.write(',')
			fp.write(x[0][1].encode('utf-8'))
			fp.write(',')
			fp.write(x[1][0].encode('utf-8'))
			fp.write(',')
			fp.write(x[1][1].encode('utf-8'))
			fp.write('\n')

#save cities code and name
list_save(_all,'_all.txt')






def read_file_to_list(filename):
	mylist=[]
	l=[]
	with open(filename,'r') as fp:
		for line in fp.readlines():
			
			mylist.append(line.split(','))

	return mylist

#'utf-8' list
#mylist=read_file_to_list('_all.txt')



##### then load _all list into Mysql!!























