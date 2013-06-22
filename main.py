# coding=gbk
# $File: main.py
# $Date: Sun Feb 24 14:47:27 2013 +0800
# $Author: ronnie.alonso@gmail.com
#
#      0. You just DO WHAT THE FUCK YOU WANT TO. 
"""
example:
usage:python main.py --port = 8000 --log_file_prefix = MCI@8000.log
"""
"""		
cookie_secret generator
import base64 
import uuid 
base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
"""
import tornado.web
import tornado.httpserver
import tornado.database
import tornado.options
import logging
import os

from admin import TimeQueryHandler,TimeHandler,MapQueryHandler,MapHandler,SettingHandler,DeleteAdminHandler,ManageHandler,RuleHandler,CheckHandler,StudentEditHandler,StudentHandler,adminHandler,AdminJaLoginHandler,AdminJaLogoutHandler
from jalogin import JaLoginHandler,JaLogoutHandler
from basic import LoginHandler , RegisterHandler , DetectCreateHandler , DetectResultHandler , CheckStatusHandler
from face import FaceppHandler , FaceRegisterHandler
from sv import SpeechTrainHandler,SpeechDetectHandler
from location import UploadLocationHandler, LocationRegisterHandler

from tornado.options import define,options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			# (r"/test", TestHandler),

			# Mobile API
			# (r"/login", LoginHandler),
			# (r"/register", RegisterHandler),
			(r"/jalogin", JaLoginHandler),
			(r"/jalogout",JaLogoutHandler),
			(r"/faceverify" , FaceppHandler),
			(r"/faceregister" , FaceRegisterHandler),
			(r"/svdetect" , SpeechDetectHandler),
			(r"/svtrain", SpeechTrainHandler),
			(r"/detectcreate", DetectCreateHandler),
			(r"/getdetectresult" , DetectResultHandler),
			(r"/uploadlocation", UploadLocationHandler),
			(r"/registerlocation", LocationRegisterHandler),
			(r"/checkstatus" , CheckStatusHandler),

			# Admin
			(r"/admin", adminHandler),
			(r"/admin/jalogin" , AdminJaLoginHandler),
			(r"/admin/logout" , AdminJaLogoutHandler),
			(r"/admin/student", StudentHandler),
			(r"/admin/student/edit", StudentEditHandler),
			(r"/admin/checkin",CheckHandler),
			(r"/admin/rule", RuleHandler),
			(r"/admin/manage", ManageHandler),
			(r"/admin/manage/delete", DeleteAdminHandler),
			(r"/admin/setting", SettingHandler),
			(r"/admin/map_stat", MapHandler),
			(r"/admin/map_stat/search", MapQueryHandler),
			(r"/admin/time_stat", TimeHandler),
			(r"/admin/time_stat/([0-9]+)", TimeQueryHandler),
		]

		settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates").encode("gbk"), 
			static_path = os.path.join(os.path.dirname(__file__), 'static').encode("gbk"),
			cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
			debug = True,
		)
		tornado.web.Application.__init__(self , handlers , **settings)
		self.db = tornado.database.Connection(host = 'localhost:3306' , database= 'mobile' , user = 'root' , password = 'sjtu2012')

if __name__ == "__main__":
	print "Welcome to Mobile Checkin Server"
	# tornado.options.parse_config_file("config.conf")
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
