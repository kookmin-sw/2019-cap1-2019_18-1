from flask import Flask,flash, render_template, request, url_for, redirect, session, abort
from flask_bootstrap import Bootstrap
import pymongo
import os

app = Flask(__name__)
Bootstrap(app)


@app.route('/', methods=["GET"])
def index():
	if not session.get('logged_in'): #로그인 되어 있지 않으면 로그인 페이지로 이동
		return render_template('login.html')
	else:
		#return render_template('logout.html') #임시
		return homepage()


#userid = request.form[id]

@app.route('/main')
def homepage():
	if session.get('logged_in'):
		client = pymongo.MongoClient('mongodb://localhost:27017')
		db = client.dust
		accountcollection = db.account
		accountresults = accountcollection.find({"idnum":session["idnum"]})
		collection = db.recent
		results = collection.find({"idnum":session["idnum"]})
		client.close()

		
		for doc in accountresults:
			acclist = list(doc.values())
		for poc in results:
			datalist = list(poc.values())
			if acclist[3] == datalist[1]:	
				return render_template('main.html', recentData=datalist, menu=1, data=1)
		return render_template('main.html', data=0) #바꿔야돼!!!!!!!!!!!!!!!!!!!!!!
	else:
		return index()


@app.route('/details')
def details():
	if not session.get('logged_in'):
		client = pymongo.MongoClient('mongodb://localhost:27017')
		db = client.dust
		icollection = db.internaldust
		ecollection = db.externaldust
		iresults = icollection.find().sort("_id",-1).limit(24)
		eresults = ecollection.find().sort("_id",-1).limit(24)
		client.close()

		pm10 = []
		pm25 = []
		date = []

		for doc in eresults:
			li = list(doc.values())
			pm10.append(li[4])
			pm25.append(li[6])
			date.append(li[8])

		return render_template('test_chart.html', epm10=pm10, epm25=pm25, edate=date, iData=iresults, title='Details', menu=2)
	else:
		return index()


"""@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name
##-------------------------

@app.route('/test', methods = ['GET'])
def test():

      user = request.args.get('myName')
      return redirect(url_for('success', name = user))

if __name__ == '__main__':
   app.run(debug = True)	
"""
@app.route('/test')
def form():
	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.dust
	collection = db.setting

	found = collection.find_one({"idnum":session["idnum"]})
	client.close()

	return render_template('control.html', menu=3, userValue=found['userValue'], optSet=found['optSet'])



@app.route('/control', methods=['POST'])
def control():
	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.dust
	collection = db.setting

	collection.update({"idnum":session["idnum"]}, {"$set": {"userValue":request.form['userValue']}})

	
	if request.form.get('optset') == 'on':
		collection.update({"idnum":session["idnum"]}, {"$set": {"optSet":'true'}})	
	else:
		collection.update({"idnum":session["idnum"]}, {"$set": {"optSet":'false'}})

	client.close()
	return form()



@app.route('/join')
def join():
	return render_template('join.html', menu=4)

@app.route('/joinus', methods=['POST'])
def joinus():

	newuserid = request.form['id']
	newuserpw = request.form['pw']
	newidnum = request.form['idnum']

	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.dust
	collection = db.account

	collection.insert({"id":newuserid, "pw":newuserpw, "idnum":newidnum})
	client.close()

	return render_template('joinus.html', firstname=newuserid)
#form action
@app.route('/hello', methods=['GET'] )
def action():
	temp1 = request.args.get('firstname')
	temp2 = request.args.get('lastname')
	temp3 = request.args.get('email')
	##firstname = request.form['firstname']
	##lastname = request.form['lastname']
	##email = request.form['email']
	return render_template('action.html', firstname=temp1, lastname=temp2, email=temp3)

#@app.route('/login')
#def login_form():
	#return render_template('login.html')

@app.route('/index', methods=['POST'])
def login():
	#폼에서 넘어온 데이터를 가져와 정해진 유저네임과 암호를 비교하고 참이면 세션을 저장한다.
	#회원정보를 DB구축해서 추출하서 비교하는 방법으로 구현 가능 - 여기서는 바로 적어 줌
	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.dust
	collection = db.account
	
	#found = collection.find({"$and":[{"id":request.form['username']}, {"password":request.form['password'] }]})
	found = collection.find()
	for doc in found:
		li = list(doc.values())
		if li[1] == request.form['username'] and li[2] == request.form['password'] :
			session['logged_in'] = True
			session['idnum'] = request.form['idnum']
			session['username'] = request.form['username']


	flash('유저네임이나 암호가 맞지 않습니다.')
	return index()




@app.route('/logout')
def logout():
	session.clear()
	#return redirect(url_for('index'))
	return index()

if __name__ == '__main__':
	app.secret_key = os.urandom(24) #좀 더 알아 볼것. 시크릿키는 세션등의 기능을 위해 반드시 필요하다.
	app.run(debug=True, host='0.0.0.0')
app.secret_key = 'sample_secret'

#if __name__=="__main__":
	#app.run(host='0.0.0.0', debug=True)