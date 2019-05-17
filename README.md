# moviebrowser
movie thumnail manager  
動画のファイル管理を一元的に行う  
<img src ="https://img.shields.io/badge/python3.4+-green.svg">
<img src ="https://img.shields.io/badge/flask-red.svg">
<img src ="https://img.shields.io/badge/bootstrap2.0-green.svg">
<img src ="https://img.shields.io/badge/MongoDB-green.svg">
<img src ="https://img.shields.io/badge/Docker-green.svg">
<img src ="https://img.shields.io/badge/Linux_Mint-v.19.1-green.svg">


2019-05-17

# Dependency
Flask  
Bootstarp  
python 3.4+  
MongoDB(on Docker)    
Linux Mint 19.1にて動作確認  

# Setup
Dockerにてmongodを起動(port 28001)  
初回のみmovie_database_make.pyを起動する。  
    1.Pathオブジェクトにメディアがあるディレクトリを指定  
    2.image_path_dirに作成したメディアのサムネイルを一時保管する場所を指定  
    3.make_thumnail = Falseにてサムネイル作成の可否  
    4.python3 movie_database_make.py  
    5.image_path_dirにできたサムネイルをzip形式にて"thumnail.zip"として圧縮  
    6.zipファイルをstatic/以下に置く  
databaseの作成は検討予定なのと、Dockerを終了するとデータベースはなくなる。  

# Usage
webブラウザー上で"localhost:5000/movieにアクセスする。  
サムネイルをクリックすると動画の再生  
NavBarにて並び替え  
検索窓にてファイルの検索  
★をクリックすると星の数（最高３）を変えることができる。０にするには星の表示をクリック  

問題点  
    *1000件が表示条件（データベースのアクセス向上の為）
    *デザイン
    *並び替えがファイルのアクセスや★の変更をすると再生回数の並び順になってしまう
# Licence
This software is released under the MIT License, see LICENSE.md.

# Authors
Burao Mima

# References
Bootstrap公式(https://getbootstrap.com/)  
Mongo公式(https://www.mongodb.com/jp)  
Flask公式(http://flask.pocoo.org/)  