# 開発環境用

import pandas as pd
from datetime import date, datetime
import gspread  # pythonでspread sheetを操作するためのライブラリ
# oauth2clientは、Googleの各種APIにアクセスするためのライブラリ
from oauth2client.service_account import ServiceAccountCredentials  # 認証情報関連

import os
from dotenv import load_dotenv
load_dotenv()

def auth():

    SP_CREDENTIAL_FILE = {
                "type": "service_account",
                "project_id": os.environ['SHEET_PROJECT_ID'],
                "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
                "private_key": os.environ['SHEET_PRIVATE_KEY'],
                "client_email": os.environ['SHEET_CLIENT_EMAIL'],
                "client_id": os.environ['SHEET_CLIENT_ID'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
    }

    # APIを使用する範囲の指定
    SP_SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    SP_SHEET_KEY = '1fWhJBRz9e2a9RmOYZ-HAQox5cMV9SLSvvVfaCTFlRTA'   # スプレッドシートのURL(~d/.../edit~の"..."部分)
    SP_SHEET = 'diary'  # 記入するシート名

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(SP_CREDENTIAL_FILE, SP_SCOPE)    # 認証情報すり合わせ
    gc = gspread.authorize(credentials) # 認証

    worksheet = gc.open_by_key(SP_SHEET_KEY).worksheet(SP_SHEET)    # SP_SHEET_KEYのSP_SHEETの情報を開いて、データを持ってくる

    return worksheet


"""
d = input("YYYYMMDDで？：")
# 日付
def diary_date(d):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())
    
    from datetime import date, datetime

    if d.isdecimal() and len(d) == 8:
        x = datetime.strptime(d, '%Y%m%d').date() 
        timestamp = x.strftime('%Y/%m/%d')
    else:
        timestamp = date.today().strftime("%Y/%m/%d")

    # dfに日付を入れる
    df = df.append({'日付': timestamp, '天気': '', '気分': '', '出来事': ''}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('日付登録しました')

weather_list = ['晴れ', '曇り', '雨', '雪', '晴れ/曇り', '晴れ/雨', '曇り/雨', 'みぞれ']
mood_list = ['😀', '😄', '😆', '😅', '😓', '😢', '😩', '😱', '😡', '😏', '😴', '😁', '😷', '🤗',]

weather = input('天気は？：')
def day_weather(weather):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
    if weather in weather_list:
        df.iloc[-1, 1] = weather

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('天気を登録しました')

mood = input('気分は？：')
def day_mood(mood):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
    if mood in mood_list:
        df.iloc[-1, 2] = mood

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('気分を登録しました')


text = input('どんな日？：')
def day_log(text):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
    df.iloc[-1, 3] = text

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('お疲れ様でした')

diary_date(d)
day_weather(weather)
day_mood(mood)
day_log(text)

"""

# text = 'あいう'
text = """20200113
晴れ
元気
昨日のオモウマい店めっちゃ面白かったー。夢の中へ素晴らしい！！！"""
try:
    t = text.split('\n')

    timestamp = date.today().strftime("%Y/%m/%d")

    if len(t) == 4:
        d = t[0]
        if len(d) == 8 and d.isdecimal():
            try:    
                from datetime import date, datetime
                x = datetime.strptime(d, '%Y%m%d').date()
                d = x.strftime('%Y/%m/%d')
            except:
                print('日付は、YYYYMMDDの８桁で入力してください。')

            w = t[1]
            m = t[2]
            l = t[3]

            # 日付が正しいとわかったら、ワークシートに記入する
            worksheet = auth()
            df = pd.DataFrame(worksheet.get_all_records())
            df = df.append({'日付': d, '天気': w, '気分': m, '出来事': l}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

            # ワークシートを更新
            worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    else:
        print('日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを↑のように改行して記入してください。')
except:
    print('日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを↑のように改行して記入してください。')

"""

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

import os
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_GSPREAD_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_GSPREAD_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return 'Hello World'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# リプライメッセージ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))

    weather_list = ['晴れ', '曇り', '雨', '雪', '晴れ/曇り', '晴れ/雨', '曇り/雨', 'みぞれ']

    if event.message.text == '今日':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    elif event.message.text in weather_list:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='天気情報です')
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='こんにちはーーー') 
        )


if __name__ == "__main__":
    app.run()

"""
