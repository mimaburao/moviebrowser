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

    form = SearchForm()
    if form.validate_on_submit():
        my_database.search = form.search.data
        form.search.data = ''
    
    data_all.clear()
    if( my_database.thumnail_images == {} ):
#        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = my_database.read_db_thumnail(data_all)
    else:
        data_all = my_database.read_db_thumnail(data_all)

    return render_template('show.html', data_all=data_all,form=form,)

@app.route('/manager', methods=['GET','POST'])
def manager(data_all=[]):
    global my_database
    my_database.search_id = request.args.get('search_item', default='', type=str)
    my_database.index_howto = request.args.get('index_sort',default='views', type=str)
   
    form = SearchForm()
    if form.validate_on_submit():
        my_database.search = form.search.data
        form.search.data = ''
    
    data_all.clear()
    if( my_database.thumnail_images == {} ):
#        put_togarther_images.set_images_from_zip_all(thumnail_images)
        data_all = my_database.read_db_thumnail(data_all)
    else:
        data_all = my_database.read_db_thumnail(data_all)
    
    sum_database_count = 0
    sum_database_count = my_database.database_sum_count()
    
    return render_template('manager.html', data_all=data_all,form=form, sum_database_count=sum_database_count)

@app.route('/rethumnail', methods=['GET','POST'])
def thumnail_rewrite():
    global my_database
    for data in my_database.find( str(request.args.get('id_number'))):
        try:
            my_database.rethumnail(data["filename"])
        except:
            pass
    my_database.index_howto = str(request.args.get("index"))
#    thumnail_image.clear()
    return redirect(url_for('manager',search_item=str(request.args.get('id_number'))))

@app.route('/play', methods=['GET','POST'])
def play():
    global my_database
    for data in my_database.find( str(request.args.get('id_number'))):
        args = ['mpv','--geometry=50%','--volume=80']
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
    return redirect(url_for('show_all'))

@app.route('/remove')
def remove():
    global my_database
    my_database.remove( str(request.args.get('id_number')) )
#    index_order = str(request.args.get("index"))
#    thumnail_images.clear()
    return redirect(url_for('manager', index_sort=str(request.args.get("index"))))


if __name__ == '__main__':
    app.run()
    joblib.dump(my_database.thumnail_images,"cache_thumnail.jb", compress=0)