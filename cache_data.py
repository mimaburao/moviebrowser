# 一時変数やデータを外部に保存する
# 巳摩
# 2019-05-24
import joblib
from pathlib import Path
from io import BytesIO
import base64

def update_thumnail_images(thumnail_file=''):
        file_data = BytesIO()
        with open(thumnail_file,"br") as file:
                file_data = base64.b64encode(file.read()).decode("utf-8")
                return file_data

