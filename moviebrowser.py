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

#mylibrary
import put_togarther_images
import movie_database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret' # CSRF対策でtokenの生成に必要
bootstrap = Bootstrap(app)

index_order = '' #並び方の記憶
thumnail_images = {}  #サムネの辞書形式での画像データ一覧

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
    global index_order
    global thumnail_images
    search = ''
    index_howto = request.args.get('index_sort',default='views', type=str)

    if( index_order != '' ):
        index_howto = index_order
        index_order = ''
    
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        form.search.data = ''
    
    data_all.clear()
    if( thumnail_images == {} ):
        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = movie_database.db_read_thumnail_all(data_all, search, index_howto, thumnail_images)
    else:
        data_all = movie_database.db_read_thumnail_all(data_all, search, index_howto, thumnail_images)

    return render_template('show.html', data_all=data_all,form=form, index_howto=index_howto)

@app.route('/manager', methods=['GET','POST'])
def manager(data_all=[]):
    global index_order
    global thumnail_images
    search = ''
    search_id = ''
    search_id = request.args.get('search_item', default='', type=str)
    index_howto = request.args.get('index_sort',default='views', type=str)

    if( index_order != '' ):
        index_howto = index_order
        index_order = ''
    
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        form.search.data = ''
    
    data_all.clear()
    if( thumnail_images == {} ):
        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = movie_database.db_read_thumnail_all(data_all, search, index_howto, thumnail_images, search_id)
    else:
        data_all = movie_database.db_read_thumnail_all(data_all, search, index_howto, thumnail_images, search_id)
    
    sum_database_count = 0
    sum_database_count = movie_database.database_sum_count()
    
    return render_template('manager.html', data_all=data_all,form=form, index_howto=index_howto, sum_database_count=sum_database_count)

@app.route('/rethumnail', methods=['GET','POST'])
def thumnail_rewrite():
    global index_order
    global thumnail_images
    for data in movie_database.find_movie_database( str(request.args.get('id_number'))):
        try:
            movie_database.rethumnail_make(data["filename"])
        except:
            pass
    index_order = str(request.args.get("index"))
    thumnail_images.clear()
    return redirect(url_for('manager',search_item=str(request.args.get('id_number'))))

@app.route('/play', methods=['GET','POST'])
def play():
    global index_order
    for data in movie_database.find_movie_database( str(request.args.get('id_number'))):
        args = ['mpv','--geometry=50%','--volume=80']
        args.append(data["filename"])
        try:
            subprocess.check_output(args)
        except:
            pass
    movie_database.countup_views(str(request.args.get('id_number')))
    index_order = str(request.args.get("index"))
    return redirect(url_for('show_all'))

@app.route('/star', methods=['GET'])
def star():
    global index_order
    index_order = str(request.args.get("index"))
    movie_database.set_star(str(request.args.get('id_number')), int(request.args.get('stars')))
    return redirect(url_for('show_all'))

@app.route('/update')
def update():
    global index_order
    global thumnail_images
    index_order = str(request.args.get("index"))
    movie_database.movie_database_update( '/mnt/drive_d/download2' )
    thumnail_images.clear()
    return redirect(url_for('show_all'))

@app.route('/remove')
def remove():
    global index_order
    global thumnail_images
    movie_database.remove_movie_database( str(request.args.get('id_number')) )
#    index_order = str(request.args.get("index"))
    thumnail_images.clear()
    return redirect(url_for('manager', index_sort=str(request.args.get("index"))))


if __name__ == '__main__':
    app.run()