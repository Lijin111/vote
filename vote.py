#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 

import socket,time,sys,traceback,random
from datetime import datetime
import utils,json
from email_kit import Email

def genCode():
	db=utils.getDB()
	for r in db["user_tbl"].all():
		code=int(random.random()*10000)
		d={}
		d["id"]=r["id"]
		d["code"]=code
		db["user_tbl"].upsert(d, ["id"])

def sendCode():
	db=utils.getDB()
	e=Email()
	#for r in db["user_tbl"].all():
	for r in db.query("select * from user_tbl"):
		#print r["user_name"]
		e.send([r["email"]],"年会投票验证码","%s,您好:<br><br>      您的验证码为：%s, 请妥为保存，在年会网上投票时使用"%(r["user_name"],r["code"]))


sendCode()




