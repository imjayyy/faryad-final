from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
import pymongo

from bson.objectid import ObjectId

from datetime import datetime,timedelta 


app = Flask(__name__)
app.secret_key = 'faryad'
connection = 'mongodb+srv://faryad:faryad@cluster0-hlef6.mongodb.net/test'
myclient = pymongo.MongoClient(connection)

mydb = myclient["Faryad"]
users = mydb["users"]
donors = mydb["donors"]
requests = mydb["requests"]
users.create_index("Email",  unique=True)


@app.route("/", methods=['Post', 'Get'])
def index():
    username = request.form.get('Username')
    password = request.form.get('password')
    donor = donors.find_one({'username': username, 'password': password})
    if donor:
        session['logged_in'] = True
        session['DonorID'] = str(donor['_id'])
        return redirect(url_for('home'))
    return render_template('Login.html')

@app.route("/home", methods=['Post', 'Get'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    areas = donors.find_one({'_id': ObjectId(session['DonorID'])})
    areas = areas['areas']
    cl = requests.find({'status':'Awaiting', 'Area':{'$in': areas}}).sort([('Date',pymongo.DESCENDING)])
    accepts, ignored = requests.count_documents( { 'status':'Accepted', 'DonorID': (session['DonorID']) } ), requests.count_documents({'status':'Awaiting', 'Area':{'$in': areas}})
    arr2= requests.find({'status':'Accepted','DonorID': str(session['DonorID'])}).sort([('Date',pymongo.DESCENDING)]).limit(5)
    return render_template('index.html', arr=cl, accepts= accepts, ignored = ignored, arr2 = arr2)


@app.route("/affirmed", methods=['Post', 'Get'])
def affirmed():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    arr2= requests.find({'status':'Accepted','DonorID': str(session['DonorID'])}).sort([('Date',pymongo.DESCENDING)])
    return render_template('requests.html', arr=arr2)

@app.route("/completed", methods=['Post', 'Get'])
def completed():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    arr2= requests.find({'status':'Delivered','DonorID': str(session['DonorID'])}).sort([('Date',pymongo.DESCENDING)])
    return render_template('completed.html', arr=arr2)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['DonorID'] = ''
    return redirect(url_for('index'))

@app.route("/saveData", methods=['Post'])
def saveData():
    data = request.get_json()
    users.insert_one(data)
    return 'Data Saved'

@app.route("/saveRequest", methods=['Post'])
def saveRequest():
    data = request.get_json()
    data['status'] =  "Awaiting"
    data['Date'] = datetime.today()
    # data["DonorID"] = donorID
    requests.insert_one(data)
    return 'Data Saved'

@app.route("/changeStatus/<ID>")
def changeStatus(ID):
    requests.update_one({'_id': ObjectId(ID)}, { "$set" :{'status': "Accepted", 'DonorID': str(session['DonorID']), 'Date Accepted': datetime.today()}})
    return ''

@app.route("/changeStatusToDelivered/<ID>")
def changeStatusToDelivered(ID):
    requests.update_one({'_id': ObjectId(ID)}, { "$set" :{'status': "Delivered", 'DonorID': str(session['DonorID']), 'Date Delivered': datetime.today()}})
    return ''

if __name__ == "__main__":
    app.run(debug=True)


        