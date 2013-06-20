Mobile Check In
基于面部识别、语音识别的移动签到APP
=============

文件列表
----------------------------

* api_test.py api测试文件
* face.py 	人脸识别模块
* facepp.py 	Face++ SDK
* model.py 	注册、登陆模块
* main.py 	主程序
* SQL.txt 	MySQL初始化语句
* location.py	地理位置注册和验证
* sv.py		语音注册和验证

API文档
----------------------------
* 登陆界面
API:    http://localhost:8000/login
POST:    {'name':'xxx','password':'xxx'}
HEADER:  {  "Content-type":"application/json",
            "Accept":"text/plain",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" }
RESPONSE:{  "error":0}
error:  0 for success
        1 for invalid password
        2 for password or username can't be empty

* 用户注册
API:    http://localhost:8000/login
POST   {'name':'xxx','password':'xxx'}
HEADER {"Content-type":"application/json",
        "Accept":"text/plain",
        "Connection": "Keep-Alive", 
        "Cache-Control": "no-cache" }
RESPONSE:{  "error":}
error:  0 for success
        1 for username exist
        2 for password or username can't be empty

* 面部验证
API http://localhost:8000/faceverify
POST:	http://localhost:8000/faceverify
		{"pic":picture_file}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":
			"similarity":}
error:	0 for success
		1 for face unrecogize
		2 for not login

Cookie should contain the response set-cookie from the sever when user login(important!)
example:	HTTP Request HEADER		
			{"Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache",
			"Cookie": client_cookie }

* 面部注册
API http://localhost:8000/faceregister
POST:	http://localhost:8000/faceregister
		{"pic":picture_file}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":
			"faceid":}

error:	0 for success
		1 for face unrecogized
		2 for not login
		3 for face_add error
		4 for already register
Cookie should contain the response set-cookie from the sever when user login(important!)
the client_cookie can get from the server's response
example:	HTTP Request HEADER		
			{"Content-type":"image/jpeg",
			"Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}

* 语音训练
API http://localhost:8000/svtrain
POST:	http://localhost:8000/svtrain
		{"voice1":voice
		"voice2":voice
		"voice3":voice
		}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":}
error:	0 for success
		1 for not login
		2:newSVEngine error
		3:speaker adapt model failed
		-1 for failure in train
备注：上传语音格式：wav格式8000hz 16bit mono

* 语音验证
API http://localhost:8000/svdetect
POST:	http://localhost:8000/svdetect
		{"voice":voice}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":}
error:	0 for success
		1 for not login
		2 for not accepted
		4:user not initialize audio
		-1 for failure in detect process

* 地理位置上传
API http://localhost:8000/uploadlocation
POST:   http://localhost:8000/uploadlocation
	{
		'latitude':latitude,
		'longitude':longitude
	}
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie}

* 地理位置注册
API http://localhost:8000/registerlocation
POST:   http://localhost:8000/registerlocation
	{
		'locid':1 
	}
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie}
备注：目前仅有SJTU，locid为1

* 创建验证
API http://localhost:8000/detectcreate
POST:   http://localhost:8000/detectcreate
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie}
RESPONSE:{  "error": }
error:  0 for success
        1 for SQL error
        2 for not login
返回set-cookie新增sessionid，需加入到http协议的cookie中

* 查询验证结果
API http://localhost:8000/getdetectresult
POST:   http://localhost:8000/getdetectresult
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie}
RESPONSE:{  "error": 0}
error:  0 for success
        1 for fail
        2 for not login
        3 for no sessionid
        4 for SQL error