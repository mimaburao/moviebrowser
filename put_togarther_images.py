#サムネイルをまとめて読み書きできるようにする
#2019-05-15
#巳摩

import zipfile
from collections import OrderedDict
import traceback
import base64
from io import BytesIO
from pathlib import Path

#画像置き場
image_path_dir = '/home/mima/work/moviebrowser/static/'

def put_togarther_images(filename):
    """thumnail.zipファイルに書き込む"""
    with zipfile.ZipFile(image_path_dir + 'thumnail.zip', 'w', compression=zipfile.ZIP_STORED) as new_zip:
        image_path =Path('/home/mima/work/moviebrowser/static/' + filename)
        if(image_path.is_file):
            new_zip.write(image_path_dir + filename, arcname=filename)

def add_zip(image_filename, image_path_tmp_dir= image_path_dir):
    """サムネイルを追加する"""
    try:
        p = Path(image_path_tmp_dir + image_filename)
        with zipfile.ZipFile(image_path_tmp_dir + 'thumnail.zip', mode="a") as zip_data, p:
            zip_data.write( image_path_tmp_dir + "tmp/" + image_filename, arcname=image_filename )
    except:
        print('Not archive')

def update_zip(image_filename='', del_thumnail=''):
    """Zip中の目的ファイルを更新する（削除して、追加する）
    del_thumnailの指定時は削除のみ
    option
    image_filename = 更新するサムネイル画像ファイル名
    del_thumnail = 削除するファイル名
    """
    try:
        zip = zipfile.ZipFile(image_path_dir + 'thumnail.zip', mode="r")
        with zip:
            zip.extractall(image_path_dir+ 'zip_tmp')
            with Path(image_path_dir+ 'zip_tmp') as p:
                for file in list(p.glob("**/*")):
                    if( str(file.name) == image_filename ):
                        file.unlink()
                    elif(str(file.name) == del_thumnail):
                        file.unlink()
        with Path(image_path_dir + 'thumnail.zip') as zip_file:
            zip_file.unlink()            
        with zipfile.ZipFile(image_path_dir + 'thumnail.zip', mode="a", compression=zipfile.ZIP_STORED) as zip_file:
            with Path(image_path_dir+ 'zip_tmp') as p:
                for file in list(p.glob("**/*")):
                    if ( file.suffix == '.jpg'):  #勝手にフォルダーを作成する対策
                        zip_file.write( image_path_dir + "zip_tmp/" + str(file.name), arcname=str(file.name) )
                if( image_filename == '' ):
                    return print("remove only")
                zip_file.write( image_path_dir + "tmp/" + image_filename, arcname=image_filename )
                print("zip: " + image_path_dir + "tmp/" + image_filename)
                #with Path(image_path_dir + "tmp/" + image_filename) as rethumnail_image_file:
                #    rethumnail_image_file.unlink()

    except:
        print('Not archive')
    return True

def read_images_from_zip(filename):
    """zipからファイル名を指定して読み込む(base64形式)"""
    file_data = BytesIO()

    try:
        with zipfile.ZipFile(image_path_dir + 'thumnail.zip', 'r') as zip_data:
            # ファイルリスト取得
            infos = zip_data.infolist()
            
            for info in infos:
                # ファイルパスでスキップ判定
                if (info.filename == filename):
                    # zipからファイルデータを読み込む(base64にてweb表示の肝みたい)
                    file_data = base64.b64encode(zip_data.read(info.filename)).decode("utf-8")
    except zipfile.BadZipFile:
        print(traceback.format_exc())

    return file_data

def set_images_from_zip_all(thumnail_images={}):
    """一気にzipのサムネイルを読み込み、辞書とする"""
    file_data = BytesIO()
    try:
        with zipfile.ZipFile(image_path_dir + 'thumnail.zip', 'r') as zip_data:
            # ファイルリスト取得
            infos = zip_data.infolist()
            
            for info in infos:
                file_data = base64.b64encode(zip_data.read(info.filename)).decode("utf-8")
                thumnail_images[info.filename] = file_data
    except zipfile.BadZipFile:
        print(traceback.format_exc())
    return thumnail_images


