#動画管理ブラウザー
#2019-05-12
#巳摩
from flask import Flask
from flask import render_template,redirect,url_for,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_bootstrap import Bootstrap
import datetime,subprocess,re
from io import BytesIO
import joblib
from pathlib import Path

#mylibrary
import put_togarther_images
import movie_database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret' # CSRF対策でtokenの生成に必要
bootstrap = Bootstrap(app)
my_database = movie_database.MovieDB('testdb','/home/mima/work/moviebrowser/static/tmp', 3, '/mnt/drive_d/download2')

class SearchForm(FlaskForm):
    """
    WTFフォームの準備クラス
    """
    search = StringField('検索ファイル名', validators=[Required()])
    submit = SubmitField('検索')

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'

@app.route('/movie', methods=['GET','POST'])
def show_all(data_all=[]):
    global my_database
    my_database.index_howto = request.args.get('index_sort',default='views', type=str)
    my_database.search_id = ''
    my_database.search = ''

#    form = SearchForm()
#    if form.validate_on_submit():
#        my_database.search = form.search.data
#        form.search.data = ''
    if(request.method == 'GET'): #検索窓の取得（何故かGETメソッド）
        my_database.search = request.args.get('search', default='', type=str)
    data_all.clear()
    if( my_database.thumnail_images == {} ):
#        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = my_database.read_db_thumnail(data_all)
    else:
        data_all = my_database.read_db_thumnail(data_all)

    return render_template('show.html', data_all=data_all)

@app.route('/manager', methods=['GET','POST'])
def manager(data_all=[]):
    global my_database
    if(my_database.search_id):  #Noneの場合の対処
        my_database.search_id = my_database.search_id
    else:
        my_database.search_id = ''
    if(request.args.get('search_item')):  ##Noneの場合の対処
        my_database.search = request.args.get('search_item', default='', type=str)
    else:
        my_database.search = ''
    my_database.index_howto = request.args.get('index_sort',default='views', type=str)
   
#    form = SearchForm()
#    if form.validate_on_submit():
#        my_database.search = form.search.data
#        form.search.data = ''
    if(request.method == 'GET'):  #検索窓の取得（何故かGETメソッド）
        my_database.search = request.args.get('search', default='', type=str)

    data_all.clear()
    if( my_database.thumnail_images == {} ):
#        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = my_database.read_db_thumnail(data_all)
    else:
        data_all = my_database.read_db_thumnail(data_all)
    
    sum_database_count = 0
    sum_database_count = my_database.database_sum_count()
    
    return render_template('manager.html', data_all=data_all, sum_database_count=sum_database_count)

@app.route('/rethumnail', methods=['GET','POST'])
def thumnail_rewrite():
    global my_database
    for data in my_database.find( str(request.args.get('id_number'))):
        try:
            my_database.rethumnail(data["filename"])
        except:
            pass
    my_database.index_howto = str(request.args.get("index"))
    joblib.dump(my_database.thumnail_images,my_database.db.name + "_cache_thumnail.jb", compress=0)
#    thumnail_image.clear()
    return redirect(url_for('manager',search_item=str(request.args.get('id_number'))))

@app.route('/remake_thumnail_all')
def remake_thumnail_all():
    global my_database
    global my_database
    for data in my_database.db.movie_client.find():
        try:
            my_database.rethumnail(data["filename"], 'Interval')
        except:
            pass
    my_database.index_howto = str(request.args.get("index"))
    joblib.dump(my_database.thumnail_images,my_database.db.name + "_cache_thumnail.jb", compress=0)
    return redirect('/manager')

@app.route('/play', methods=['GET','POST'])
def play():
    global my_database
    for data in my_database.find( str(request.args.get('id_number'))):
        args = ['mpv','--geometry=70%','--volume=80']
        args.append(data["filename"])
        try:
            subprocess.check_output(args)
        except:
            pass
    my_database.countup_views(str(request.args.get('id_number')))
    my_database.index_howto = str(request.args.get("index"))
    return redirect(url_for('show_all'))

@app.route('/star', methods=['GET'])
def star():
    global my_database
    my_database.index_howto = str(request.args.get("index"))
    my_database.set_star(str(request.args.get('id_number')), int(request.args.get('stars')))
    return redirect(url_for('show_all'))

@app.route('/update')
def update():
    global my_database
    my_database.index_howto = str(request.args.get("index"))
    my_database.update()
    joblib.dump(my_database.thumnail_images,my_database.db.name + "_cache_thumnail.jb", compress=0)
    return redirect(url_for('show_all'))

@app.route('/remove')
def remove():
    global my_database
    my_database.remove( str(request.args.get('id_number')) )
    joblib.dump(my_database.thumnail_images,my_database.db.name + "_cache_thumnail.jb", compress=0)
    #index_order = str(request.args.get("index"))
#    thumnail_images.clear()
    return redirect(url_for('manager', index_sort=str(request.args.get("index"))))

@app.route('/select_database', methods=['GET','POST'])
def select_db():
    global my_database
    databases = []
    media_select_dir = ''
    if(request.method == 'GET'):  #選択した動画の場所
        media_select_dir = str(request.args.get("media_dir"))
    databases = movie_database.get_database_info()

    if(request.method == 'POST'):
        if(request.form["create_db"]):
            database_new_name = request.form["database_name"]
            if (database_new_name != ''):  #新規データベース
                my_database.__init__(database_new_name, './static/tmp', 3, str(request.args.get("media_dir")))
                my_database.make_database()
        return redirect(url_for('show_all'))
    
    return render_template('select_database.html', databases = databases, media_select_dir= media_select_dir)

@app.route('/choose_dir')
def choose_dir():
    file_infos = []
    file_dir = ''
    if(request.args.get("choice_dir") == ".."):  #上層に移動
        with Path(request.args.get("file_dir")) as p:
            file_dir = str(p.parent.resolve())
            for file_info in list (p.parent.glob("*")):
                if((Path(str(file_info))).is_dir()):
                    file_infos.append(str(file_info))
            return render_template('/choose_dir.html', file_infos=file_infos, file_dir=file_dir)
    
    if(request.args.get("choice_dir")):  #指定階層
        with Path(str(request.args.get("choice_dir"))) as p:
            file_dir = str(p.resolve())
            print(file_dir)
            for file_info in list(p.glob("*")):
                if((Path(str(file_info))).is_dir()):
                    file_infos.append(str(file_info))
        return render_template('/choose_dir.html', file_infos=file_infos, file_dir=file_dir)

    with Path.cwd() as p: #最初の階層
        with Path(str(p.resolve())) as p_abs:
            file_dir = str(p_abs)
            for file_info in list(p_abs.glob("*")):
                if(Path(str(file_info)).is_dir()):
                    file_infos.append(str(file_info))
            return render_template('/choose_dir.html', file_infos=file_infos,file_dir=file_dir)

@app.route('/check_db')    
def check_db():
    global my_database

    if ( request.args.get("database_name") ):  #従来のデータベース
        my_database.__init__(str(request.args.get("database_name")), './static/tmp', 3, request.args.get("media_dir"))
        return redirect(url_for('show_all'))
    else:
        return redirect(url_for('select_db'))

if __name__ == '__main__':
    app.run()
    joblib.dump(my_database.thumnail_images,my_database.db.name + "_cache_thumnail.jb", compress=0)