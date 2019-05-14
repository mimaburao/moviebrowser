#動画データベース作成とサムネイル作成
#2019-05-12

from pathlib import Path
import datetime
import subprocess
import struct
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:28001/')

# Pathオブジェクトを生成
p = Path("/mnt/drive_e/drive_e/tmp")

#画像置き場
image_path_dir = '/home/mima/work/moviebrowser/static/'

# 再帰的な検索
with client:

    db = client.testdb
    db.movie_client.remove()

    i = 0
    for data in list(p.glob("**/*")):
    	args = ['ffprobe', '-v', 'error', '-i', str(data), '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1']
    	duration_time = 0
    	try:
    		res = subprocess.check_output(args)
    		duration_time = float(res.decode('utf8')) #再生時間数
    		for j in range(1,4):  #三コマのサムネイル切り出し
    		    cut_time = duration_time * j / 4
    		    print(cut_time)
    		    cut_args = ['ffmpeg', '-ss', str(int(cut_time)),'-t','1','-r','1','-i', str(data), str(data) + str(j) +'.jpg']
    		    subprocess.check_output(cut_args)
    		thumnal_args = ['montage', str(data) + '1' + '.jpg', str(data) + '2' + '.jpg', str(data) + '3' + '.jpg', '-tile', 'x1', '-geometry', '120x120+1+1', image_path_dir + (data.name).replace(" ","") + '.jpg'] #半角スペース対策済み
    		subprocess.check_output(thumnal_args) #各動画サムネ作成
    		for j in range(1,4): #切り出したサムネイル削除
    		    thumnail_cut_file = Path(str(data) + str(j) + '.jpg')
    		    thumnail_cut_file.unlink()
    	except:
    		print ("Error.")
    	db.movie_client.insert_one({"filename": str(data), "views": 0, "star": 0, "thumnail_file": (data.name).replace(" ","") +'.jpg', "date": data.stat().st_ctime, "duration": duration_time, "access_time": data.stat().st_atime, "size": data.stat().st_size}) #半角スペース対策済み

    for data in db.movie_client.find():
    	print (data) #日付はdatetimeの形で登録されているので正しい　2019-05-11
    	