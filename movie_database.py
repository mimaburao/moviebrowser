#動画データベース作成とサムネイル作成
#2019-05-12
#対象ファイルはメディア系コンテンツのみ
#サムネイル作成時のみ再生時間取得
#クラス化　2019-05-25

from pathlib import Path
import datetime,subprocess,struct
from pymongo import MongoClient
import pymongo
import sys,random,base64,joblib
from bson.objectid import ObjectId
from io import BytesIO


#my library
import put_togarther_images

class MovieDB:
    '''
    データベースの管理
    search : 文字検索
    search_id : Mongo "_id"による検索
    make_thumnail : サムネを作成するかどうか
    thumnail_frames : 動画のサムネの数
    media_dir : 動画の場所
    thumnail_images : サムネ画像の保存（辞書形式）
    client : Mongoのアクセス用
    db : Mongoデータベースの名前
    '''
    search = ''
    search_id=''
    index_howto='views'
    image_path_tmp_dir = ''
    make_thumnail_flag = True
    thumnail_frames = 3
    media_dir = ''
    thumnail_images={}
    client = MongoClient('mongodb://localhost:28001/')
    db = client['testdb']
    
    def __init__(self,database_name = 'testdb',image_path_tmp_dir = '/home/mima/work/moviebrowser/static/tmp',thumnail_frames = 3, media_dir = '/mnt/drive_d/download2'):
        '''
        image_path_tmp_dir : サムネの一時ファイル
        thumnail_frames :　サムネの数
        '''
        self.image_path_tmp_dir = image_path_tmp_dir
        self.thumnail_frames = thumnail_frames
        self.media_dir = media_dir
        self.db = self.client[database_name]
        print("Database_name:" + self.db.name)
        print("media_dir:" + self.media_dir)
        with Path(self.db.name + "_cache_thumnail.jb") as p:  #サムネキャッシュの読み込み
            if( p.is_file() ):
                print("read thumnail")
                self.thumnail_images = joblib.load(str(p))
    
    def media_file_suffix(self,suffix):
        """メディアファイル判定"""
        mediafile = ['.mp4','.avi','.mkv', '.ts']
        for media_flag in mediafile:
            if(suffix == media_flag):
                return True
        return False

    def read_db_thumnail(self,data_all=[]):
        """
        データベースとサムネイルを読み込む
        data_all : web表示用のデータ
        """
        if( self.search_id == ''):
            cursor = self.db.movie_client.find({"filename": { '$regex': '.*' + self.search + '.*'}}).sort(self.index_howto, pymongo.DESCENDING).limit(1000)
        else:
            cursor = self.find(self.search_id)
        for data in cursor:
            images_data = self.thumnail_images.get(data["thumnail_file"]) #サムネの画像を持っているか
            data["thumnail_file"] = "data:image/png;base64,{}".format(images_data)
            data["date"] = datetime.datetime.fromtimestamp(data["date"])
            data["access_time"] = datetime.datetime.fromtimestamp(data["access_time"])
            data["duration"] = datetime.timedelta(seconds= int(data["duration"]))
            data["size"] = int(data["size"] / 1024 /1024) #Mbの表示のため
            data_all.append(data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
        return data_all

    def __make_thumnail(self, media_file='', thumanil_type='Random'):
        """サムネイルの作成し、再生時間を取得
        media_file :　動画ファイル
        """
        with Path(media_file) as data:
            args = ['ffprobe', '-v', 'error', '-i', str(data), '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1']
            duration_time = float(0)
            try:
                i = 0
                if( self.make_thumnail_flag and self.media_file_suffix( data.suffix ) ):
                    res = subprocess.check_output(args)
                    duration_time = float(res.decode('utf8')) #再生時間数
                    for i in range(1,self.thumnail_frames + 1):  #三コマのサムネイル切り出し
                        print (i)
                        if( thumanil_type == 'Random'):
                            cut_time = random.randint(0,int(duration_time))
                        else:
                            cut_time = duration_time * i / (self.thumnail_frames + 1)
                        cut_args = ['ffmpeg', '-ss', str(int(cut_time)),'-t','1','-r','1','-i', str(data), str(data) + str(i) +'.jpg']
                        subprocess.check_output(cut_args)
                    thumnal_args = ['montage', str(data) + '1' + '.jpg', str(data) + '2' + '.jpg', str(data) + '3' + '.jpg', '-tile', 'x1', '-geometry', '120x68', '-background','None',self.image_path_tmp_dir + '/' +(data.name).replace(" ","") + '.png'] #半角スペース対策済み
                    subprocess.check_output(thumnal_args) #各動画サムネ作成
                    for i in range(1,self.thumnail_frames + 1): #切り出したサムネイル削除
                        thumnail_cut_file = Path(str(data) + str(i) + '.jpg')
                        thumnail_cut_file.unlink()
                else:
                    print ("Not thumnail file")
            except:
                print ("Error.")
        return duration_time

    def make_database(self):
        """
        初めてのデータベース作成
        p : メディアの場所
        """
        self.db.movie_client.remove()
        self.thumnail_images.clear()
        duration_time = float(0)
        with Path(self.media_dir) as p:
            print("making database:"+str(p))
            for data in list(p.glob("**/*")):
                if( data.is_file() and self.media_file_suffix( data.suffix )):
                    if(self.make_thumnail_flag):
                        duration_time = self.__make_thumnail( str(data) , 'Interval')
                        self.thumnail_images[(data.name).replace(" ","") +'.png'] = self.read_thumnail_image(self.image_path_tmp_dir + '/' +(data.name).replace(" ","") +'.png')
                    else:
                        print("Don't make thumnail")
                    self.db.movie_client.insert_one({"name": str(data.name),"filename": str(data), "views": 0, "star": 0, "thumnail_file": (data.name).replace(" ","") +'.png', "date": data.stat().st_ctime, "duration": duration_time, "access_time": data.stat().st_atime, "size": data.stat().st_size}) #半角スペース対策済み
            for data in self.db.movie_client.find():
                print (data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
        return True

    def remove(self,id_number=''):
        """Mongoの_id情報よりデータベースとサムネを削除する
        """
        for data in self.db.movie_client.find({"_id": ObjectId(id_number)}):
            put_togarther_images.update_zip( '',data["thumnail_file"] )
            del self.thumnail_images[data["thumnail_file"]]
        self.db.movie_client.delete_one( {"_id": ObjectId(id_number)})
        return True

    def read_thumnail_image(self,thumnail_file=''):
        '''
        サムネ画像を読み込む
        '''
        file_data = BytesIO()
        try:
            with Path(thumnail_file) as file:
                file_data = base64.b64encode(file.read_bytes()).decode("utf-8")
                return file_data
        except:
            print("not fount")
            file_data=b''
            return file_data

    def update(self):
        """データベースより新しいメディアファイルがあればデータベース更新"""
        p = Path(self.media_dir)
        with p:
            cursor = self.db.movie_client.find().sort("date", pymongo.DESCENDING).limit(1)
            for cursor_data in cursor:
                for data in list(p.glob("**/*")):
                    if( self.media_file_suffix( data.suffix ) ):
                        if( data.stat().st_ctime > cursor_data["date"] ):
                            duration_time = float(0)
                            if( data.is_file() and self.media_file_suffix( data.suffix )):
                                duration_time = self.__make_thumnail(str(data), 'Interval')
                                #put_togarther_images.add_zip( (data.name).replace(" ","") + '.jpg' )
                                self.thumnail_images[(data.name).replace(" ","") + '.png'] = self.read_thumnail_image( self.image_path_tmp_dir + '/' + (data.name).replace(" ","") + '.png' )
                                self.db.movie_client.insert_one({"name": str(data.name),"filename": str(data), "views": 0, "star": 0, "thumnail_file": (data.name).replace(" ","") +'.png', "date": data.stat().st_ctime, "duration": duration_time, "access_time": data.stat().st_atime, "size": data.stat().st_size}) #半角スペース対策済み
                                #            put_togarther_images.put_togarther_images((data.name).replace(" ","") + '.jpg')
                            else:
                                print(data.name)
        return True

    def rethumnail(self,filename='', thumnail_type = 'Random'):
        """
        サムネイル再作成
        filename: 動画ファイル
        thumanil_type = 'InterVal' 等間隔作成
                      = 'Random' ランダム作成
        """
        file_data = Path(filename)
        with file_data:
            duration_time = float(0)
            duration_time = self.__make_thumnail(str(file_data), thumnail_type )
            self.db.movie_client.update({"filename": str(file_data)},{"$set": {"duration": duration_time}})
            self.db.movie_client.update({"filename": str(file_data)}, {"$set": {"thumnail_file": (file_data.name).replace(" ","") + '.png'}})  #サムネをjpgで登録している場合の対策
            put_togarther_images.update_zip((file_data.name).replace(" ","") + '.png')
            self.thumnail_images[(file_data.name).replace(" ","") + '.png'] = self.read_thumnail_image(self.image_path_tmp_dir + '/' + (file_data.name).replace(" ","") + '.png')
        return True

    def find(self,id_number=''):
        """_idよりデータベース検索"""
        cursor = self.db.movie_client.find({"_id" : ObjectId(id_number)})
        return cursor
    
    def set_star(self,id_number='', star=0):
        """starを記録（最高３）"""
        self.db.movie_client.update({"_id" : ObjectId(id_number)}, {'$set': {'star': star}})
        return True
    
    def countup_views(self,id_number='', views=0):
        """再生数を数える"""
        self.db.movie_client.update({"_id" : ObjectId(id_number)}, {'$inc': {'views': 1}})
        return True
    
    def database_sum_count(self):
        """データベースの件数を数える"""
        return self.db.movie_client.find().count()    

    def __del__(self):
        self.client.close()

def get_database_info():
    """
    Mongoのデータベース情報取得
    戻り値　{データベース名 : 動画の場所}
    """
    db_names= []
    databases_info = []
    with MongoClient('mongodb://localhost:28001/') as client:
        db_names = client.list_database_names()
        for db_name in list(db_names):
            db = client[db_name]
            for data in db.movie_client.find().limit(1):
                with Path(data["filename"]) as file:
                    db_media_dir = str(file.parents[0])
                    databases_info.append({"name": db_name, "media_dir": db_media_dir})
    return databases_info

def main(argv):
    """
    option
    argv = 動画ファイルの場所(最後の/は必要ない)
    """
    p = Path(argv[0])
    image_path_tmp_dir = '/home/mima/work/moviebrowser/static/tmp'  #サムネイル画像置き場(最後の/は必要ない)
    thumnail_frames = 3

    my_database = MovieDB('testdb',image_path_tmp_dir, thumnail_frames, str(p) )
    my_database.make_database()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except:
        print("探索する場所を指定してください(最後の/は必要ない)")   	