#動画管理ブラウザー
#2019-05-12
#巳摩
from flask import Flask
from flask import render_template
from flask import request
from pymongo import MongoClient
import datetime

app = Flask(__name__)
client = MongoClient('mongodb://localhost:28001/')
db = client.testdb

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'

@app.route('/movie')
def show(data_all=[],image_filenames=[]):
    for data in db.movie_client.find():
        data_all.append(data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
    for image_data in db.movie_client.find({},{ "_id": 0, "thumnail_file": 1 }):
        my_dic = {}
        print(image_data["thumnail_file"])
        my_dic['image_name'] = 'static/' + str(image_data["thumnail_file"])
        image_filenames.append(my_dic)
    return render_template('show.html', data_all=str(data_all), image_filenames = image_filenames)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=["巳摩","貴之"]):
    return render_template('index.html', name=name)


@app.route('/username/<name>')
def show_user_profile(name):
    return render_template('index.html', name=name)

@app.route('/post', methods=['POST'])
def show_post():
    name = request.form.getlist('name')
    return render_template('index.html', name=name)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # this is executed if the request method was GET or the
    # credentials were invalid

if __name__ == '__main__':
    app.run()