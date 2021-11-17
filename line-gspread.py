# 開発環境用

import pandas as pd
from datetime import date
import gspread  # pythonでspread sheetを操作するためのライブラリ
# oauth2clientは、Googleの各種APIにアクセスするためのライブラリ
from oauth2client.service_account import ServiceAccountCredentials  # 認証情報関連

def auth():
    SP_CREDENTIAL_FILE = 'line-gspread-c4b007d26ebe.json'

    # APIを使用する範囲の指定
    SP_SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    SP_SHEET_KEY = '1fWhJBRz9e2a9RmOYZ-HAQox5cMV9SLSvvVfaCTFlRTA'   # スプレッドシートのURL(~d/.../edit~の"..."部分)
    SP_SHEET = 'diary'  # 記入するシート名

    credentials = ServiceAccountCredentials.from_json_keyfile_name(SP_CREDENTIAL_FILE, SP_SCOPE)    # 認証情報すり合わせ
    gc = gspread.authorize(credentials) # 認証

    worksheet = gc.open_by_key(SP_SHEET_KEY).worksheet(SP_SHEET)    # SP_SHEET_KEYのSP_SHEETの情報を開いて、データを持ってくる

    return worksheet



# 日付
def diary_date():
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    timestamp = date.today().strftime("%Y/%m/%d")

    # "今日"の日記ですか？-->> いいえであれば、
    # timestamp = input('YYYY/MM/DDで入力して: ')

    # dfに日付を入れる
    df = df.append({'日付': timestamp, '天気': '', '気分': '', '出来事': ''}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('日付登録しました')


def day_weather():
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
    df.iloc[-1, 1] = '晴れ'

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('天気を登録しました')



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
