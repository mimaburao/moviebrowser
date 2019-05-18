#動画管理ブラウザー
#2019-05-12
#巳摩
from flask import Flask
from flask import render_template,redirect,url_for,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_bootstrap import Bootstrap
from bson.objectid import ObjectId
from pymongo import MongoClient
import pymongo
import datetime,subprocess,re
from io import BytesIO

#mylibrary
import put_togarther_images

app = Flask(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret' # CSRF対策でtokenの生成に必要
bootstrap = Bootstrap(app)
client = MongoClient('mongodb://localhost:28001/')
db = client.testdb

index_order = '' #並び方の記憶
thumnail_images = {}  #サムネの辞書形式での画像データ一覧

class SearchForm(FlaskForm):
    search = StringField('検索ファイル名', validators=[Required()])
    submit = SubmitField('検索')

#サムネイル一覧を辞書として保存している場合
def db_read_thumnail_all(data_all=[], search=None, index_howto='views', thumnail_images={}):
    if(search == None):
        cursor = db.movie_client.find().sort(index_howto, pymongo.DESCENDING)
        for data in cursor:
            images_data = thumnail_images.get(data["thumnail_file"]) #サムネの情報を持っているか
            data["thumnail_file"] = "data:image/png;base64,{}".format(images_data)
            data["date"] = datetime.datetime.fromtimestamp(data["date"])
            data["access_time"] = datetime.datetime.fromtimestamp(data["access_time"])
            data["duration"] = datetime.timedelta(seconds= data["duration"])
            data["size"] = int(data["size"] / 1024 / 1024) #Mbの表示のため
            data_all.append(data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
        return data_all
    else:
        cursor = db.movie_client.find({"filename": { '$regex': '.*' + search + '.*'}}).sort(index_howto, pymongo.DESCENDING)
        for data in cursor:
            images_data = thumnail_images.get(data["thumnail_file"]) #サムネの情報を持っているか
            data["thumnail_file"] = "data:image/png;base64,{}".format(images_data)
            data["date"] = datetime.datetime.fromtimestamp(data["date"])
            data["access_time"] = datetime.datetime.fromtimestamp(data["access_time"])
            data["duration"] = datetime.timedelta(seconds= data["duration"])
            data["size"] = int(data["size"] / 1024 /1024) #Mbの表示のため
            data_all.append(data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
        return data_all

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'

@app.route('/movie', methods=['GET','POST'])
def show_all(data_all=[]):
    global index_order
    global thumnail_images
    search = ''
    index_howto = request.args.get('index_sort',default='views', type=str)
    if( index_order != '' ):
        print(index_order)
        index_howto = index_order
        index_order = ''
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        form.search.data = ''
    data_all.clear()
    if( thumnail_images == {} ):
        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = db_read_thumnail_all(data_all, search, index_howto, thumnail_images)
    else:
        data_all = db_read_thumnail_all(data_all, search, index_howto, thumnail_images)

    return render_template('show.html', data_all=data_all,form=form, index_howto=index_howto)

@app.route('/play', methods=['GET','POST'])
def play():
    global index_order
    for data in db.movie_client.find({"_id" : ObjectId(str(request.args.get('id_number')))}):
        args = ['mpv','--geometry=50%','--volume=80']
        args.append(data["filename"])
        try:
            subprocess.check_output(args)
        except:
            pass
    db.movie_client.update({"_id" : ObjectId(str(request.args.get('id_number')))}, {'$inc': {'views': 1}})
    index_order = str(request.args.get("index"))
    return redirect(url_for('show_all'))

@app.route('/star', methods=['GET'])
def star():
    global index_order
    index_order = str(request.args.get("index"))
    db.movie_client.update({"_id" : ObjectId(str(request.args.get('id_number')))}, {'$set': {'star': int(request.args.get('stars'))}})
    return redirect(url_for('show_all'))

@app.route('/username/<name>')
def show_user_profile(name):
    return render_template('index.html', name=name)

@app.route('/post', methods=['POST'])
def show_post():
    name = request.form.getlist('name')
    return render_template('index.html', name=name)


if __name__ == '__main__':
    app.run()