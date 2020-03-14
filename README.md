# moviebrowser
movie thumnail manager  
動画のサムネイルを見て、再生できるようにするwebアプリ  
<img src ="https://img.shields.io/badge/python3.4+-green.svg">
<img src ="https://img.shields.io/badge/flask-red.svg">
<img src ="https://img.shields.io/badge/bootstrap4.0-green.svg">
<img src ="https://img.shields.io/badge/MongoDB-green.svg">
<img src ="https://img.shields.io/badge/Docker-green.svg">
<img src ="https://img.shields.io/badge/Linux_Mint-v.19.3-green.svg">


![sample](images/moviebrowser_sample01.mp4.gif)
# Dependency
Flask 1.0+ 
Bootstarp 4(flask-bootstrap)  
python 3.4+
- pymongo,joblib,memory-tempfile  
  
MongoDB 3.6+(on Docker)  
ffmpeg  
Imagemagick-6+  
mpv  
SMPlayer  
Linux Mint 19.3にて動作確認  

# Setup
ソフトウェアの管理にて、ffmepg,ImageMagick,mpvをインストール
pip3にてflask-bootstrap,pymongo,joblib,memory-tempfileのインストール(うまく行かない場合は後述の注意点を参照)
Dockerにてmongodを起動(port 28001, static/dbにボリュームマウント)
mongo.shに参考の起動方法  
※memory_tempfileは現在（2019-06-02）そのままでは動かない。[修正方法](https://qiita.com/mimaburao/items/26e1463feb6397197232)  
※memory_tempfile2.2.2（2020-02-01）の修正版では問題ないようだ。  

* 初期化  
python3 movibrowser.pyと実行する。  
右上のプルダウンで「データベースの変更」を選択する。  
新規データベース名をフォームに適当に入れて、「動画場所選択」をクリックする。  
動画が保存されているディレクトリーまで移動できたら、「メディア場所決定」ボタンをクリックする。  
新規データベース名とディレクトリーが有ること確認して「データベース作成」ボタンをクリックする。
するとデータベースとサムネイル自動で作成するので待つ。  
データベース構築後、データベース名が更新されているので作成したデータベースのボタンをクリックする。  
サムネイルとファイル名等が一覧表示される。別の動画保存場所がある場合は繰り返す。  

# Usage
python3 moviebrowser.pyと実行する。
webブラウザー上で"localhost:5000/movieにアクセスする。  
サムネイルをクリックすると動画の再生  
各項目クリックにて並び替え（降冪順）  
検索窓にてファイルの検索  
★をクリックすると星の数（最高３）を変えることができる。０にするには星の表示をクリック  
NavBarのプルダウン「更新」で、メディアファイルの更新作業  
NavBarのプルダウン「管理」で、サムネイルをクリックするとランダムでサムネイルを作成  
NavBarのプルダウン「管理」で、ファイル名をクリックするとデータを削除  
NavBarのプルダウン「データベースの変更」で、新規データベースと既存のデータベースの切り替え  
- 「動画場所選択」にて動画の場所を指定する
    - 「上位階層に移動」で親ディレクトリ
    - ディレクトリのクリックで、ディレクトリに行ける
    - 「メディア場所決定」で表示のディレクトリにて検索を行うようにする
- 「新規データベース名」に名前を付けて、「データベース作成」すると指定のディレクトリのデータベースを作成する
- データベース名にて「選択有無」をクリックすると指定のデータベースに移行できる


## 問題点  
 
- デザイン
- (ffmpegにて)再生できない動画はサムネが作成されない
- 動画再生がmpvになる

# 注意点
- インストール時にうまく行かない場合はpipが古い場合がある。
 - pip3 install --upgrade pip setuptools
 - とする。または、--userがないと注意されることもある。
 - pip3 install --user インストールするモジュール(pymongo,flask-bootstap等)  
- サムネが表示されない場合はImageMagick,ffmpegのインストールを再確認して下さい
- 動画再生はmpvといソフトに依存しています
# Licence
This software is released under the MIT License, see LICENSE.md.

# Authors
Burao Mima

# References
Bootstrap公式(https://getbootstrap.com/)  
Mongo公式(https://www.mongodb.com/jp)  
Flask公式(http://flask.pocoo.org/)  