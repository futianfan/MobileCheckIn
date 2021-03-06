# coding=utf-8
from tornado.escape import url_unescape,utf8
from basic import BaseHandler
import datetime 
import random,string,json
from jaccount import encrypt , decrypt , find , splitdata
from setting import siteID,port,domain

def datetime_handler(obj):
	if hasattr(obj, 'isoformat'):
		return obj.isoformat()
	elif isinstance(obj, None):
		return None
	else:
		raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

"""Admin Main Page
http://domain:port/admin
"""
class adminHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			if self.get_cookie('login')=='1':
					self.render("login.html", notification = "密码错误")
			else:
				self.render("login.html", notification = "请输入用户名和密码")
		else:
			self.redirect("/admin/index")

	def post(self):
		username=self.get_argument('username',None)
		password=self.get_argument('password',None)
		if username and password:
			sql= "SELECT UID,CHINAME FROM ADMINISTRATOR WHERE \
					USERNAME=\'%s\' AND PASSWORD=\'%s\';" %(username,password)
			info = self.db.query(sql)
			if info:
				info = info[0]
				self.set_cookie('login','0')
				self.set_secure_cookie('uid',str(info['UID']))
				if(info['CHINAME']):
					self.set_secure_cookie('chiname', info['CHINAME'])
				self.redirect('/admin')
				return
		self.set_cookie('login','1')
		self.redirect('/admin')

"""Admin Jaccount Login Page
http://domain:port/admin/jalogin
"""
class AdminJaLoginHandler(BaseHandler):
	def get(self):
		if not self.get_arguments('jatkt'):
			uaBaseURL="http://jaccount.sjtu.edu.cn/jaccount/"
			returl = 'http://'+domain+':'+str(port)+'/admin/jalogin'
			iv = string.join(random.sample('1234567890abcdef',8),'')
			# print "iv:" , iv
			self.set_secure_cookie('iv' , iv , None)
			redirectURL =  uaBaseURL + "jalogin?sid="+siteID+"&returl="+encrypt(returl,iv)+"&se="+encrypt(iv,iv)
			self.redirect(redirectURL)
		else:
			try:
				if len(self.get_argument('jatkt')) == 0:
					raise tornado.web.HTTPError(404)
			except TypeError:
				raise tornado.web.HTTPError(404)
			iv = self.get_secure_cookie('iv')
			jatkt = self.get_argument('jatkt')
			data = decrypt(jatkt,iv)
			data = find(data,ur'ja[\s\S]*')
			# utf-8编码
			data.decode('utf-8')
			ProfileData = splitdata(data)
			if self.checkUser(ProfileData):
				self.set_secure_cookie('uid' , ProfileData['id'] , None)
				self.set_secure_cookie('chiname', ProfileData['chinesename'],None)
				self.set_cookie('login','0')
				if ProfileData['ja3rdpartySessionID'] != iv:
					self.write('Hacking Attempt~!')
					return
			else:
				self.set_cookie('login','1')
			self.redirect('/admin')

	def checkUser(self , profile):
		uid = profile['id']
		info = self.db.query('SELECT UID,CHINAME,USERNAME FROM ADMINISTRATOR WHERE UID = %s;' % (uid))
		if info:
			if(not info[0]['CHINAME'] or not info[0]['USERNAME']):
				sql = 'UPDATE ADMINISTRATOR SET CHINAME=\'%s\' , USERNAME=\'%s\' WHERE UID = %s;' \
										% (profile['chinesename'],profile['uid'],uid)
				res = self.db.execute(sql)
			return 1
		else:
			return 0

"""Admin Jaccount Logout Page
http://domain:port/admin/jalogout
"""
class AdminJaLogoutHandler(BaseHandler):
	def get(self):
		if self.get_secure_cookie('iv'):
			uaBaseURL="http://jaccount.sjtu.edu.cn/jaccount/"
			returl = 'http://'+domain+':'+str(port)+'/admin'
			iv = self.get_secure_cookie('iv')
			redirectURL =  uaBaseURL + "ulogout?sid="+siteID+"&returl="+encrypt(returl,iv)
			self.clear_all_cookies()
			self.redirect(redirectURL)
			return
		self.clear_all_cookies()
		self.redirect('/admin')
		return

"""Student Information Page
http://domain:port//admin/student
"""
class StudentHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			info=[]
			q=""
			self.clear_header("Content-Type")
			self.set_header("Content-Type", "application/json")
			if self.get_argument('op',None) and self.get_argument('q',None):
				option=self.get_argument('op',None)
				q=self.get_argument('q',None)
				info = self.query(option,q)
				self.write(json.dumps(info))
			else:
				self.write("Missing Argument!")
			return

	def query(self,option,q):
		url_unescape(q,'utf-8')
		if(option == 'option1'):
			info = self.db.query('SELECT U.UID,U.USERNAME,U.CHINAME,D.DETECTTIME,D.STATUS FROM USER U LEFT OUTER JOIN \
								DETECT D ON U.UID = D.OWNER WHERE U.CHINAME=\'%s\'' % (q))
		elif(option == 'option2'):
			info = self.db.query('SELECT U.UID,U.USERNAME,U.CHINAME,D.DETECTTIME,D.STATUS FROM USER U LEFT OUTER JOIN \
								DETECT D ON U.UID = D.OWNER WHERE U.UID=%s' % (q))
		elif(option == 'option3'):
			info = self.db.query('SELECT U.UID,U.USERNAME,U.CHINAME,D.DETECTTIME,D.STATUS FROM USER U LEFT OUTER JOIN \
								DETECT D ON U.UID = D.OWNER WHERE U.USERNAME=\'%s\'' % (q))
		for item in info:
			item['DETECTTIME'] = datetime_handler(item['DETECTTIME'])

		return info

"""Student Information Edit API
http://domain:port/admin/student/edit?uid=...&dt=...&op=...
"""
class StudentEditHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			if (self.get_argument('uid',None) and 
						self.get_argument('op',None)):
				uid=str(self.get_argument('uid',None))
				dt=self.get_argument('dt',None)
				op=self.get_argument('op',None).replace("T"," ")
				if(op == '1'):
					sql = 'UPDATE DETECT SET STATUS=0 WHERE\
					 OWNER=%s AND DETECTTIME=\'%s\';' % (uid,dt)
					info = self.db.execute(sql)
					self.write("0")
				elif(op == '2'):
					sql = 'UPDATE USER SET IMAGESAMPLE=NULL, \
								LOCID=NULL, AUDIOENGINE=NULL WHERE \
								UID = %s;' % uid
					info = self.db.execute(sql)
					self.write("0")
				elif(op == '3' and dt):
					sql = "DELETE FROM DETECT WHERE OWNER=%s AND DETECTTIME=\'%s\';" % (uid,dt)
					info = self.db.execute(sql)
					self.write("0")
				else:
					self.write("-1")
			else:
				self.write("-1")

from datetime import datetime
"""Show Detect Status Page
http://domain:port/admin/checkin
"""
class CheckHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			info=[]
			start=""
			terminal=""
			if self.get_argument('start',None) and self.get_argument('terminal',None):
				start=self.get_argument('start',None)
				terminal=self.get_argument('terminal',None)
				info = self.query(start,terminal)
				self.write(json.dumps(info))
			else:
				self.write("Missing Argument!")
			return
	
	def query(self,start,terminal):
		start = self.date2time(start," 00:00:00")
		terminal = self.date2time(terminal ,' 23:59:59')
		sql='SELECT U.UID,U.USERNAME,U.CHINAME,D.DETECTTIME,D.STATUS,U.DEPARTMENT \
		 		FROM USER U, DETECT D WHERE U.UID = D.OWNER AND \
		 			D.DETECTTIME <= \'%s\' AND D.DETECTTIME >=\'%s\';' % (terminal,start)
		info = self.db.query(sql)

		for item in info:
			item['DETECTTIME'] = datetime_handler(item['DETECTTIME'])

		return info

	def date2time(self,date,miniute):
		date = date.replace('/','-')
		date = datetime.strptime(date, "%m-%d-%Y")
		date = date.strftime("%Y-%m-%d")
		date = date + miniute
		return date

class DefaultRuleHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			info = {}
			startime = ""
			termtime = ""

			sql = "SELECT STARTTIME,TERMITIME FROM LOCATION WHERE LOCATIONNAME = 'SJTU';"
			default = self.db.query(sql)
	
			if default:
				startime = default[0]["STARTTIME"]
				termtime = default[0]["TERMITIME"]
	
			info["STARTTIME"] = datetime_handler(startime)
			info["TERMITIME"] = datetime_handler(termtime)

			self.write(json.dumps(info))

		return

"""Set Checkin Time Rule Page
http://domain:port/admin/rule?start= &terminal=
"""
class RuleHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			info=[]

			if self.get_argument('start',None) and self.get_argument('terminal',None):
				start=self.get_argument('start',None)
				terminal=self.get_argument('terminal',None)
				info = self.query(start,terminal)

			self.write(json.dumps(info))

			return

	def query(self,start,terminal):
		start = self.date2time(start," 00:00:00")
		terminal = self.date2time(terminal ,' 23:59:59')
		sql = "UPDATE LOCATION SET STARTTIME = \"%s\",TERMITIME= \"%s\" \
			WHERE LOCATIONNAME = 'SJTU';" % (start,terminal)
		info=self.db.execute(sql)
		return info

	def date2time(self,date,miniute):
		date = date.replace('/','-')
		date = datetime.strptime(date, "%m-%d-%Y")
		date = date.strftime("%Y-%m-%d")
		date = date + miniute
		return date

"""Set Administrator List Page
http://domain:port/admin/manage
"""
class ManageHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			info=[]
			StuID=""
			if self.get_argument('number',None):
				StuID=self.get_argument('number',None)
				res = self.add_admin(StuID)
			chiname = self.get_secure_cookie("chiname")
			info = self.query()

			self.write(json.dumps(info))
			
			return
	
	def query(self):
		sql='SELECT * FROM ADMINISTRATOR;'
		info = self.db.query(sql)
		return info

	def add_admin(self,StuID):
		sql='SELECT UID FROM ADMINISTRATOR WHERE UID=%s;' %StuID
		res = self.db.query(sql)
		if not res:
			sql='INSERT INTO ADMINISTRATOR(UID) VALUES(%s);' % StuID
			info = self.db.execute(sql)
			return 0
		return -1

"""Add Administrator List Page
http://domain:port/admin/addadmin
"""
class AddAdminHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			StuID=""
			res = -1
			if self.get_argument('number',None):
				StuID=self.get_argument('number',None)
				res = self.add_admin(StuID)
			self.write({'error':res})

			return
	
	def add_admin(self,StuID):
		sql='SELECT UID FROM ADMINISTRATOR WHERE UID=%s;' %StuID
		res = self.db.query(sql)
		if not res:
			sql='INSERT INTO ADMINISTRATOR(UID) VALUES(%s);' % StuID
			info = self.db.execute(sql)
			return 0
		return -1

"""Delete Administrator API
http://domain:port/admin/manage/delete?uid=...
"""
class DeleteAdminHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.write("2")
		else:
			uid = self.get_argument('uid')
			sql='DELETE FROM ADMINISTRATOR WHERE UID=%s;' % uid
			res = self.db.execute(sql)
			if not res:
				self.write('0')
			else:
				self.write('1')

"""Reset Administrator Password Page
http://domain:port/admin/manage/setting
"""
class SettingHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			uid = self.get_secure_cookie('uid')
			psw=""
			alert=""
			if self.get_argument('psw1',None):
				psw=self.get_argument('psw1',None)
				res = self.set_password(psw,uid)
				if res:
					alert="密码修改失败！"
				else:
					alert="密码修改成功！"

			self.write(alert)
			
			return

	def set_password(self,psw,uid):
		sql = "UPDATE ADMINISTRATOR SET PASSWORD=\'%s\' WHERE UID=%s;"\
					% (psw,uid)
		res = self.db.execute(sql)
		return res

""" Handle JSON datetime """
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

"""Map Statistics Search API
http://domain:port/admin/map_stat/search?start=...&terminal=...
"""
class MapQueryHandler(BaseHandler):	
	def get(self):
		if not self.current_user:
			self.write({"error":-1})
		else:
			info=[]
			start=""
			terminal=""
			if self.get_argument('start',None) and self.get_argument('terminal',None):
				start=self.get_argument('start',None)
				terminal=self.get_argument('terminal',None)
				info = self.query(start,terminal)
		info = json.dumps(info,cls=ComplexEncoder)
		# print info		
		self.write(info)

	def query(self,start,terminal):
		start = self.date2time(start," 00:00:00")
		terminal = self.date2time(terminal ,' 23:59:59')
		sql='SELECT U.CHINAME,D.LONGITUDE,D.LATITUDE,D.DETECTTIME \
		 		FROM USER U, DETECT D WHERE U.UID = D.OWNER AND \
		 			D.DETECTTIME <= \'%s\' AND D.DETECTTIME >=\'%s\' AND D.STATUS=0;' % (terminal,start)
		info = self.db.query(sql)
		return info

	def date2time(self,date,miniute):
		date = date.replace('/','-')
		date = datetime.strptime(date, "%m-%d-%Y")
		date = date.strftime("%Y-%m-%d")
		date = date + miniute
		return date

"""Chart Statistics Search API
http://domain:port/admin/time_stat/([0-9]+)
"""
class TimeQueryHandler(BaseHandler):
	def get(self,op):
		if not self.current_user:
			self.redirect("/admin")
		else:
			if (op=="1"):
				sql="SELECT DATE_FORMAT(D.DETECTTIME,\'%%H\') TIMES,\
					COUNT(*) NUMS FROM DETECT D,LOCATION L WHERE \
					D.DETECTTIME>=L.STARTTIME AND D.DETECTTIME<=L.TERMITIME\
					AND L.LOCID=1 AND D.STATUS=0 GROUP BY TIMES;"
				info = self.db.query(sql)
				self.write(json.dumps(info))
			elif (op=="2"):
				sql="SELECT DATE_FORMAT(D.DETECTTIME,\'%%m\') TIMES,\
					COUNT(*) NUMS FROM DETECT D,LOCATION L WHERE \
					D.DETECTTIME>=L.STARTTIME AND D.DETECTTIME<=L.TERMITIME\
					AND L.LOCID=1 AND D.STATUS=0 GROUP BY TIMES;"
				info = self.db.query(sql)
				self.write(json.dumps(info))
			else:
				self.write('-1')

"""
Admin Index
http://domain:port/admin/index
"""
class AdminIndexHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/admin")
		else:
			print self.get_template_path()
			chiname = self.get_secure_cookie("chiname")
			self.render("index.html", chiname=chiname)
			return
