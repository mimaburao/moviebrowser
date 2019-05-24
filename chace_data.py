# 一時変数やデータを外部に保存する
# 巳摩
# 2019-05-24
import joblib
from pathlib import Path
from io import BytesIO
import base64

#画像置き場
image_path_dir = '/home/mima/work/moviebrowser/static/'

def chace_data(data):
    '''
    data　格納したいデータ
    '''
    joblib.dump(data,'thumnail_cache.jb', compress=0)

def update_thumnail_images(thumnail_images=(), thumnail_file=''):
    file_data = BytesIO()
    with Path(thumnail_file) as p:
        with p.open() as file:
            file_data = base64.b64encode(file.readbytes()).decode("utf-8")
            thumnail_images["thumnail_file"] = file_data
    return thumnail_images


