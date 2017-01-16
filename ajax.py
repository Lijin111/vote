# -*- coding: UTF-8 -*-

from bottle import *
import dataset,os, json
import utils, datetime,time


@route('/vote', method=['GET','POST'])
def vote():
	db=utils.getDB()	
	session=request.environ.get('beaker.session')
	userID=session["userID"]
	ids=request.forms.get("ids", "")
	print "ids",ids
	idList=ids.split(',')
	if len(idList)>4: return "一次投票不能超过3人"
	for r in db["user_tbl"].find(id=userID):
		if r["flag"]==1: return "您不能重复投票"

	for id in idList:
		try:
			actor=int(id)
			print "actor",actor
			d={}
			d["user_id"]=userID
			d["actor_id"]=actor
			db["vote_tbl"].upsert(d, ["id"])
		except:continue

	d={}
	d["id"]=userID
	d["flag"]=1
	db["user_tbl"].upsert(d, ["id"])
	
	return ""


@route('/getUserInfo', method=['GET','POST'])
def getInfo():
	db=utils.getDB()	
	session=request.environ.get('beaker.session')
	userID=session["userID"]
	rows = db["user_tbl"].find(id=userID)
	response.set_header("Content-Type", "application/json") 
	return utils.dumpjson(rows)


@route('/getActors', method=['GET','POST'])
def getActor():
	db=utils.getDB()	
	session=request.environ.get('beaker.session')
	rows = db.query("select * from actor_tbl order by flag, id")
	response.set_header("Content-Type", "application/json") 
	return utils.dumpjson(rows)

@route('/getActorBoard', method=['GET','POST'])
def getActor():
	db=utils.getDB()	
	session=request.environ.get('beaker.session')
	rows=[]
	for r in db["actor_tbl"].all():
		r["vote"]=utils.sql2Val(db,"select count(*) from vote_tbl where actor_id=%d"%(r["id"]))
		rows.append(r)
	rows=sorted(rows,reverse=True, cmp=lambda x,y:cmp(x["vote"],y["vote"]))
	response.set_header("Content-Type", "application/json") 
	return utils.dumpjson(rows)

