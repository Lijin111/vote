# -*- coding: UTF-8 -*-

from bottle import *
from beaker.middleware import SessionMiddleware
import dataset,os
import utils
from ajax import *

@route('/check_login', method='POST')
def do_login():
	code = request.forms.get('code')
	try:
		c = int(code)
	except:
		return "验证码错误"

	db = utils.getDB()
	for r in db.query("select * from user_tbl where code=%s" % (code)):
		session = request.environ.get('beaker.session')
		session["userID"] = r["id"]
		session["userName"] = r["user_name"]
		return ""
	return "验证码错误"


@route('/')
def get():
	redirect("/pages/vote.htm")


@route('/pages/<filename:path>')
def server_static(filename):
	return static_file(filename, root=os.path.join(utils.getConfig('env', 'docbase', r'/home/work/vote'), 'pages'))


@route('/docs/<filename:path>')
def server_static(filename):
	return static_file(filename, root=os.path.join(utils.getConfig('env', 'docbase', r'/home/work/vote'), 'docs'))


@hook('before_request')
def checkLogin():
	if request.method == "POST": return
	url = request.urlparts.path
	if url == "/pages/login.htm": return
	if not (url.endswith(".htm") or url.endswith(".html")): return
	if not url.startswith("/pages"): return

	session = request.environ.get('beaker.session')
	if not ("userID" in session):
		session["redirctUrl"] = url
		redirect("/pages/login.htm")
	else:
		userID = session["userID"]
		session["userID"] = userID


session_opts = {
	'session.type': 'file',
	'session.cookie_expires': 3000,
	'session.data_dir': './session',
	'session.auto': True
}

debug(True)
app = SessionMiddleware(app(), session_opts)
if __name__ == "__main__":
    # Interactive mode
    #run(app=app,host='0.0.0.0', port=8080, reloader=True)
    run(app=app,server='tornado',host='0.0.0.0', port=8081, reloader=True)
else:
    # Mod WSGI launch
    os.chdir(os.path.dirname(__file__))
    application = app