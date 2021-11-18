# Herokuデプロイ用

import pandas as pd
from datetime import date, datetime
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


"""
# 日付
def diary_date(d):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())
    
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

weather = input('天気は？：')
def day_weather(weather):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
    df.iloc[-1, 1] = weather

    # ワークシートを更新
    worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

    print('天気を登録しました')

mood = input('気分は？：')
def day_mood(mood):
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())

    # dfに値を入れる(dfの値の取得は、iloc[row, column])
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

# diary_date(d)
# day_weather(weather)
# day_mood(mood)
# day_log(text)

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


"""
# メッセージが送られたら、実行される
    webhookURLに、"herokuアプリのURL/callback" を紐付けしたため、
    メッセージが送られたら、このwebhookURLが呼ばれる = callback関数が実行される
"""
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
    """
    # おうむ返しする(返答内容は、event.message.textの部分で指定)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))   # event.message.textは、送信されたテキスト
    """

    text = event.message.text
    if text[:2] == '天気':

        worksheet = auth()
        df = pd.DataFrame(worksheet.get_all_records())
        df = df.append({'日付': date.today(), '天気': text[3:], '気分': '', '出来事': ''}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

        # ワークシートを更新
        worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='お疲れ様でした。明日もとりあえず生きていきましょう！！'))   # event.message.textは、送信されたテキスト
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='天気 晴れ\nのように入力してください')
        )

    # try:
    #     t = text.splitlines()

    #     if len(t) == 4:
    #         d = t[0]
    #         if len(d) == 8 and d.isdecimal():
    #             try:    
    #                 from datetime import date, datetime
    #                 x = datetime.strptime(d, '%Y%m%d').date()
    #                 d = x.strftime('%Y/%m/%d')
    #             except:
    #                 line_bot_api.reply_message(
    #                     event.reply_token,
    #                     TextSendMessage(text='日付は、YYYYMMDDの８桁で入力してください。'))   # event.message.textは、送信されたテキスト
                
    #             w = t[1]
    #             m = t[2]
    #             l = t[3]

    #             # 日付が正しいとわかったら、ワークシートに記入する
    #             worksheet = auth()
    #             df = pd.DataFrame(worksheet.get_all_records())
    #             df = df.append({'日付': d, '天気': w, '気分': m, '出来事': l}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

    #             # ワークシートを更新
    #             worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)
                
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='お疲れ様でした。明日もとりあえず生きていきましょう！！'))   # event.message.textは、送信されたテキスト
                
    #     else:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを例のように改行して記入してください。'))   # event.message.textは、送信されたテキスト
                
    # except:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを例のように改行して記入してください。'))   # event.message.textは、送信されたテキスト
        

    # # # 日付
    # if (len(event.message.text) == 8 and event.message.text.isdecimal()) or event.message.text == 'today':
    #     diary_date(event.message.text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='どんな1日でしたか')
    #     )
    # else:
    #     day_log(event.message.text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='おうむするしか！！')
    #     )

    # elif event.message.text in weather_list:  # 天気
    #     day_weather(event.message.text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=f'{event.message.text}だったんですねー！')
    #     )
    # elif event.message.text == 'mood':  # 気分
    #     day_mood(event.message.text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='そんな気分でしたか')
    #     )
    # else:
    #     day_log(event.message.text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='お疲れ様でしたー！とりあえず明日も生きよう！！！')
    #     )

if __name__ == "__main__":
    # 本番環境用
    port = os.getenv('PORT')    # Heroku上の環境変数PORTを取得
    app.run(host='0.0.0.0', port=port)  # 本番環境用のhostとportを設定
