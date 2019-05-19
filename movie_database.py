#動画データベース作成とサムネイル作成
#2019-05-12
#対象ファイルはメディア系コンテンツのみ
#サムネイル作成時のみ再生時間取得

from pathlib import Path
import datetime
import subprocess
import struct
from pymongo import MongoClient
import pymongo
import put_togarther_images
import sys
from bson.objectid import ObjectId

#メディアファイル判定
def media_file_suffix(suffix):
    mediafile = ['.mp4','.avi','.mkv', '.ts']
    for media_flag in mediafile:
        if(suffix == media_flag):
            return True
    return False

# 再帰的な検索
def make_database( p, image_path_dir, make_thumnail, thumnail_frames):
    client = MongoClient('mongodb://localhost:28001/')
    with client:
        db = client.testdb
        db.movie_client.remove()
        for data in list(p.glob("**/*")):
            args = ['ffprobe', '-v', 'error', '-i', str(data), '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1']
            duration_time = float(0)
            if( data.is_file() and media_file_suffix( data.suffix )):
                db.movie_client.insert_one({"name": str(data.name),"filename": str(data), "views": 0, "star": 0, "thumnail_file": (data.name).replace(" ","") +'.jpg', "date": data.stat().st_ctime, "duration": duration_time, "access_time": data.stat().st_atime, "size": data.stat().st_size}) #半角スペース対策済み
                #            put_togarther_images.put_togarther_images((data.name).replace(" ","") + '.jpg')
            else:
                print(data.name)
            try:
                if( make_thumnail and media_file_suffix( data.suffix ) ):
                    res = subprocess.check_output(args)
                    duration_time = float(res.decode('utf8')) #再生時間数
                    for i in range(1,thumnail_frames + 1):  #三コマのサムネイル切り出し
                        cut_time = duration_time * i / (thumnail_frames + 1)
                        print(cut_time)
                        cut_args = ['ffmpeg', '-ss', str(int(cut_time)),'-t','1','-r','1','-i', str(data), str(data) + str(i) +'.jpg']
                        subprocess.check_output(cut_args)
                    thumnal_args = ['montage', str(data) + '1' + '.jpg', str(data) + '2' + '.jpg', str(data) + '3' + '.jpg', '-tile', 'x1', '-geometry', '120x120+1+1', image_path_dir + (data.name).replace(" ","") + '.jpg'] #半角スペース対策済み
                    subprocess.check_output(thumnal_args) #各動画サムネ作成
                    for i in range(1,thumnail_frames + 1): #切り出したサムネイル削除
                        thumnail_cut_file = Path(str(data) + str(i) + '.jpg')
                        thumnail_cut_file.unlink()
                    db.movie_client.update({"filename": str(data)},{"$set": {"duration": duration_time}})
                else:
                    continue
            except:
                print ("Error.")
        for data in db.movie_client.find():
            print (data) #日付はdatetimeの形で登録されているので正しい　2019-05-11

#サムネイル一覧を辞書として保存している場合
def db_read_thumnail_all(data_all=[], search=None, index_howto='views', thumnail_images={}):
    client = MongoClient('mongodb://localhost:28001/')
    with client:
        db = client.testdb
        cursor = db.movie_client.find({"filename": { '$regex': '.*' + search + '.*'}}).sort(index_howto, pymongo.DESCENDING)
        for data in cursor:
            images_data = thumnail_images.get(data["thumnail_file"]) #サムネの画像を持っているか
            data["thumnail_file"] = "data:image/png;base64,{}".format(images_data)
            data["date"] = datetime.datetime.fromtimestamp(data["date"])
            data["access_time"] = datetime.datetime.fromtimestamp(data["access_time"])
            data["duration"] = datetime.timedelta(seconds= data["duration"])
            data["size"] = int(data["size"] / 1024 /1024) #Mbの表示のため
            data_all.append(data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
    return data_all

def find_movie_database(id_number=''):
    client = MongoClient('mongodb://localhost:28001/')
    with client:
        db = client.testdb
        cursor = db.movie_client.find({"_id" : ObjectId(id_number)})
    return cursor

def set_star(id_number='', star=0):
    client = MongoClient('mongodb://localhost:28001/')
    with client:
        db = client.testdb
        db.movie_client.update({"_id" : ObjectId(id_number)}, {'$set': {'star': star}})
    return True

def countup_views(id_number='', views=0):
    client = MongoClient('mongodb://localhost:28001/')
    with client:
        db = client.testdb
        db.movie_client.update({"_id" : ObjectId(id_number)}, {'$inc': {'views': 1}})
    return True

def main(argv):
    # Pathオブジェクトを生成
    p = Path(argv[0])
    #画像置き場
    image_path_dir = '/home/mima/work/moviebrowser/static/tmp/'
    #サムネイルの作成可否
    make_thumnail = False
    thumnail_frames = 3

    make_database( p, image_path_dir, make_thumnail,thumnail_frames)

if __name__ == "__main__":
#movie_database_make.py path
    try:
        main(sys.argv[1:])
    except:
        print("探索する場所を指定してください(最後の/は必要ない)")   	