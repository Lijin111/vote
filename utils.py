#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
import os,sys,hashlib,urllib
import logging
import time,datetime,json,struct
import traceback

import ConfigParser
cf = ConfigParser.ConfigParser()
here = os.path.dirname(__file__)
path = os.path.join(here,"config.ini")
cf.read(path)


def checkParam(p):
	return p

def initlog(logfile):
	logger = logging.getLogger(logfile)
	hdlr = logging.FileHandler(logfile)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.NOTSET)
	logger.root.setLevel(logging.NOTSET)
	return logger

def 	getPathFromUrl(url):
	i=url.find("//")	
	if i>0: url=url[i+2:]
	i=url.find("\\")	
	if i>0: url=url[i+2:]
	i=url.find("/")	
	if i>0: url=url[i+1:]
	return url

def 	getConfig(section,item, default=''):
        if cf.has_option(section, item): return cf.get(section,item)
	else: return default
		

def	mysleep(n):
	time.sleep(n)


def  	procException(logger):
	traceback.print_exc()
	logger.error("exception:"+str(sys.exc_info()[1]))


def 	removefile(path):
	os.system("rm -rf "+path)

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))


def decodeUrl(url):
        url = url.encode("GBK")
        url=urllib.unquote(url)
        #filepath=url[url.find('@')+1:]
        
        url = url.decode('UTF-8')
        url = url.encode("GBK")
	url=repr(url)
	return url[1:-1]

import dataset
db=None
def getDB():
	global db
	toConnect=0
	if db==None: toConnect=1
	else:
		try:
			r=db.query("select NOW()")
		except:
			toConnect=1
	if toConnect==1:
		dbUrl=getConfig("db", "url")
		db=dataset.connect(dbUrl)
	return db

def sql2Val(db, sql):
	for r in db.query(sql):
		for v in r: return r[v]



import decimal
def gencsv(rows, cols):
		s='{"total":%d,"rows":['%(rows.count)
		i=0
		for r in rows:
			if i!=0: s+=','
			s+='{'
			j=0
			for c in cols:
				if not (c in r): continue
				if j>0: s+=','
				t=type(r[c])
				if t==type(1) or  t==type(1.0) or t==decimal.Decimal:
					s+='"%s":%d' %(c, r[c])
				elif t==type(None):
					s+='"%s":""' %(c)
				else:
					s0='"%s":"%s"' %(c, r[c])
					s+=s0.replace('\n', '\\n')
				j+=1
			s+='}'
			i+=1
		s+=']}'
		return s


def genjson(rows, cols):
		s='{"data":['
		i=0
		for r in rows:
			if i!=0: s+=','
			s+='{'
			j=0
			for c in cols:
				if not (c in r): continue
				if j>0: s+=','
				t=type(r[c])
				if t==type(1) or  t==type(1.0) or t==decimal.Decimal:
					s+='"%s":%d' %(c, r[c])
				elif t==type(None):
					s+='"%s":""' %(c)
				else:
					val='%s'%(r[c])
					val=val.replace('\\', '\\\\')
					val=val.replace('"', r'\"')
					s0='"%s":"%s"' %(c, val)
					s+=s0.replace('\n', '\\n')
				j+=1
			s+='}'
			i+=1
		s+=']}'
		return s

def dumpjson(rows):
		s='['
		i=0
		for r in rows:
			if i!=0: s+=','
			s+='{'
			j=0
			for c in r.keys():
				if j>0: s+=','
				t=type(r[c])
				#print repr(t), repr(r[c])
				if t==list:
					s+='"%s":%s' %(c, dumpjson(r[c]))
				elif t==type(1) or  t==type(1.0) or type==long or t==decimal.Decimal:
					s+='"%s":%d' %(c, r[c])
				elif t==datetime.date:
					s+='"%s":"%d/%d/%d"' %(c,r[c].month,r[c].day,r[c].year)
				elif t==type(None):
					s+='"%s":""' %(c)
				elif t==str and len(r[c])==1:
					b=struct.unpack("B",r[c])
					s+='"%s":"%d"' %(c, b[0])
				else:
					val='%s'%(r[c])
					val=val.replace('\t', ' ')
					val=val.replace('\\', '\\\\')
					val=val.replace('"', r'\"')
					s0='"%s":"%s"' %(c, val)
					s+=s0.replace('\n', '\\n')
				j+=1
			s+='}'
			i+=1
		s+=']'
		return s


def convertDateString(s):
	if s=="": return "1900-1-1"
	pos=s.find("T")
	if (pos>=0): return s[:pos]
	else: return s

def	getFileInfohash(hfile):
	SHAhash = hashlib.sha1()
	while 1:
			buf = hfile.read(4096)
			if not buf : break
			SHAhash.update(hashlib.sha1(buf).hexdigest())
	return SHAhash.hexdigest()


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
		if not obj: return ""
		t=type(obj)
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif t==type(1) or  t==type(1.0) or t==decimal.Decimal:
			return "%d"%(obj)
		else:
			return json.JSONEncoder.default(self, obj)


