# RMsystem version 4.2

エッサの練習メニューを、組合せ最適化で計算するアプリです。

練習組みが大変な構成の公演ならば、時間短縮効果は大きいでしょう。（20年度卒から4公演連続して構成がシンプルですが…汗）

ちなみにRMは最初に組み合わせアルゴリズムを開発した人のイニシャルです。


# Demo

工事中

# Features

バージョン4.2はSlackBotであり、入力をGoogleスプレッドシートから行います。

これまでのローカル実行のバージョンに比べ、使い回すことと、入力量をへらすことに特化しています。


# Requirement

必要なライブラリは以下の通りです。

* slackbot 1.0.0
* pandas 1.2.4
* gspread 3.7.0
* oauth2client 4.1.3
* pulp 2.4

また以下の2つのファイルをgitignoreしています。別途Authorに連絡してください。
* es-spreadsheet-rmsystem-1d49147d5dc7.json
* slackbot_settings.py

1つ目がスプレッドシートにアクセスするための秘密鍵、2つ目がAPIトークンを記したセッティングファイルです。秘密鍵はGoogleCloudPlatformで入手します。

# Usage(test)

ローカルでの実行方法は以下です。
```bash
git clone https://github.com/oz-piita/es-slackbot-RMsystem
```
slackbot_settings.pyを直下に、秘密鍵をpluginsに追加します。

settings.pyは以下のようにしておきます。
```
API_TOKEN = "Past Your Slackbot APItoken Here !!!"
DEFAULT_REPLY = "あの…どうも…"
PLUGINS = ['plugins']
```
run.pyを起動します
```bash
python run.py
```
Botが起動したらSlackのBotに対して
```
@RMsystem d1
```
などとメッセージを送信することで、計算結果を文書の形で返信します。

繰り返しますがスプレッドシート側の入力はドライブのマニュアルを読んでください。

# How to deploy to Heroku

testで起動を確認できたらCtrl+Cで落として、Herokuのデプロイに移ります。Procfileやrequirements.txtはすでに作成してあります。

HerokuCLIがインストールされている状態で以下のように進めます

```bash
heroku login
```
Webブラウザからログインします

以下を一つずつ実行します。【hoge】は【】なしで適当な言葉に置き換えてください

```bash
heroku create 【Heroku上のアプリケーション名】
git add .
git commit -m "【コメント】"
heroku git:remote -a 【Heroku上のアプリケーション名】
git push heroku master
```
WebブラウザからHerokuの該当アプリケーションページに移動し、Resourcesタブからアプリケーションを起動します。

以上の手順で、Herokuの無料枠で利用できるはずです。

# Note

核になっている組合せ最適化処理はmy_calcファイルにモジュール化されています。ドライブの別のデモデータを試すときは、適当に加工してこのモジュールに喰わせてください。

データ加工はmy_inputを参考にしてください。

# Author

アプリケーション部分
* taipi(13th)

最適化アルゴリズム部分
* ryo(11th)

連絡が必要な場合は、座長に相談してください。Googleグループから連絡を取れるはずです。
