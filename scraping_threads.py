
#-*- coding:utf-8 -*-
import requests
import cookielib
import json
from bs4 import BeautifulSoup
from time import sleep
import random
import csv
import datetime

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


def get_price(conCity,conCounty,shipperCity,shipperCounty):
	form_data={'priceQueryVo.conCity':conCity,'priceQueryVo.conCounty':conCounty,
'priceQueryVo.shipperCity':shipperCity,'priceQueryVo.shipperCounty':shipperCounty}
#print form_data
	r=requests.post(url_query,headers=headers,data=form_data)
	a=json.loads(r.text)

	shipperCity=a['priceQueryVo']['shipperCity']
	shipperCounty=a['priceQueryVo']['shipperCounty']
	conCity=a['priceQueryVo']['conCity']
	conCounty=a['priceQueryVo']['conCounty']

	price=a['priceTimeVos']

	for x in price:
		if x['transportType']=='ONTIME':
			startPrice=x['startPrice']
			heavyPrice=x['heavyPrice']
			lightPrice=x['lightPrice']
			deliveryTime=x['deliveryTime']#char
#print conCity,shipperCity,startPrice,heavyPrice,lightPrice
	return (conCity,conCounty,shipperCity,shipperCounty,deliveryTime,startPrice,heavyPrice,lightPrice)


############
import Queue
import threading
import pymysql

queue = Queue.Queue()
out_queue = Queue.Queue()

#generate queue from db :  return a list
def gen_queue(num1,num2):
	#conn = pymysql.connect(host='127.0.0.1',user='root', passwd='123456', db='mysql', charset='utf8')
	#cur = conn.cursor()
	#cur.execute("USE scrapy")
	cur.execute("select fromcity,fromcountry,tocity,tocountry from cc where id>=%s and id<%s",(num1,num2))
	cc_list=cur.fetchall() # tuple()
	#cur.close()
	#conn.close()
	return cc_list




# get queue, deal, put out_queue
class ThreadUrl(threading.Thread):
	def __init__(self, queue, out_queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.out_queue = out_queue

	def run(self):
		i=0
		while True:
			i+=1
			if(i%50==0):
				_id=threading.current_thread().getName()
				print "the thread:",_id,"scraping another 50 times!",i
				sleep(random.uniform(1,1.5))

			
			
			try:
				cc = self.queue.get()
				data=get_price(*cc)  #data=(u'\u5317\u4eac\u5e02', u'\u4e1c\u57ce\u533a', u'\u5317\u4eac\u5e02', u'\u4e1c\u57ce\u533a', 15.0, 0.6, 132.0)
				self.out_queue.put(data)
			except Exception, e:
				#print "ThreadUrl get_price() error!"
				#print "%s"%(str(e))
				pass

			

			self.queue.task_done()
			#_id=threading.current_thread().getName()
			#print _id,i




# get out_queue, deal
class DatamineThread(threading.Thread):
	def __init__(self, out_queue):
		threading.Thread.__init__(self)
		self.out_queue = out_queue

	def run(self):
		i=0
		begin=datetime.datetime.now()
		conn = pymysql.connect(host='127.0.0.1',user='root', passwd='123456', db='mysql', charset='utf8')
		conn.ping(True)
		cur = conn.cursor()
		cur.execute("USE scrapy")
		while True:
			i+=1
			chunk = self.out_queue.get()
			#self.out_queue.task_done()
			###get the final data then load into db  #####def func():
			sqli="insert into final_data(fromcity,fromcountry,tocity,tocountry,deliveryTime,min_price,heavy_good,light_good) values(%s,%s,%s,%s,%s,%s,%s,%s)"
			try:
				cur.execute(sqli,(chunk[0].encode('utf-8'),chunk[1].encode('utf-8'),chunk[2].encode('utf-8'),chunk[3].encode('utf-8'),chunk[4].encode('utf-8'),chunk[5],chunk[6],chunk[7]))
				cur.execute("commit")

			except Exception, e:
				print "DatamineThread insert error!"
				#print "%s"%(str(e))
				#print chunk

			#check if lost connection to Mysql
			if(i%50==0):
				_id=threading.current_thread().getName()
				print 'mysql threads:',_id,'already insert ',i,' times!'
				try:
					cur.execute("select 1 from final_data")
					a=cur.fetchone()
					#print "cur.fetchone()=",a
					check=a[0]
					if(check==1):
						print _id,'db insert threads connected ok!'
				except:
					print _id,"seems lost connection to MySQL!"
					#cur.execute("select count(1) from final_data")
					#print _id,cur.fetchone()
					conn = pymysql.connect(host='127.0.0.1',user='root', passwd='123456', db='mysql', charset='utf8')
					conn.ping(True)
					cur = conn.cursor()
					cur.execute("USE scrapy")
				
			self.out_queue.task_done()
			#_id=threading.current_thread().getName()
			#print _id,i



def goscrapy():
	
	
	for i in range(10):
		t=ThreadUrl(queue,out_queue)
		t.setDaemon(True)
		t.start()

	for i in range(10):
		dt = DatamineThread(out_queue)
		dt.setDaemon(True)
		dt.start()


	cc_list=gen_queue(37450,1000000)#12054784=6054784+6000000   #1w 
	for cc in cc_list:
		queue.put(cc)
	print "queue is ready!"

	#wait until processing finish	
	queue.join()
	out_queue.join()



## main
begin=datetime.datetime.now()
conn = pymysql.connect(host='127.0.0.1',user='root', passwd='123456', db='mysql', charset='utf8')
#conn.ping(True)
cur = conn.cursor()
cur.execute("USE scrapy")

goscrapy()

end=datetime.datetime.now()
print 'Total times used:',(end-begin)
cur.close()
conn.close()







