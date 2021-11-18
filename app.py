# Herokuデプロイ用

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
                "private_key": os.environ['SHEET_PRIVATE_KEY'].replace('\\n', '\n'),
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

from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

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

    text = event.message.text
    try:
        t = text.splitlines()

        if len(t) == 3:
            from datetime import datetime, date
            d = date.today().strftime("%Y/%m/%d")
            w = t[0]
            m = t[1]
            l = t[2]

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'worksheetが読み込めないの？\n\n{len(t)}こに分かれます\n天気:{w}\n日時:{d}, mood: {m}\nどんな日でしたか\n{l}')
            )

            # 日付が正しいとわかったら、ワークシートに記入する
            worksheet = auth()

            df = pd.DataFrame(worksheet.get_all_records())
            df = df.append({'日付': d, '天気': w, '気分': m, '出来事': l}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

            # ワークシートを更新
            worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='３項目(天気、気分、出来事)入力してください')
            ) 
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='天気\n気分\nどんな日だったか\n\nを↑のように改行して記入してください。')
        )


        # 4行で来ていれば、spread sheetに書き込み準備
        # if len(t) == 4:
        #     d = t[0]    
        #     if len(d) == 8 and d.isdecimal():
        #         try:    
        #             x = datetime.strptime(d, '%Y%m%d').date()
        #             d = x.strftime('%Y/%m/%d')

        #             w = t[1]
        #             m = t[2]
        #             l = t[3]

                    # # 日付が正しいとわかったら、ワークシートに記入する
                    # worksheet = auth()
                    # df = pd.DataFrame(worksheet.get_all_records())
                    # df = df.append({'日付': d, '天気': w, '気分': m, '出来事': l}, ignore_index=True)   # ignore_index: append時に要素番号を新たに振りなおしてくれる

                    # # ワークシートを更新
                    # worksheet.update([df.columns.values.tolist()]+df.values.tolist())  # worksheetを更新(上のcl+vの情報を上書き)


    #             except:
    #                 line_bot_api.reply_message(
    #                     event.reply_token,
    #                     TextSendMessage(text='日付は、YYYYMMDDの８桁で入力してください。')
    #                 )



    #     # 4行でなければ
    #     else:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを↑のように改行して記入してください。')
    #         )
    # except:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='日付(YYYYMMDD)\n天気\n気分\nどんな日だったか\n\nを↑のように改行して記入してください。')
    #     )

if __name__ == "__main__":
    # 本番環境用
    port = os.getenv('PORT')    # Heroku上の環境変数PORTを取得
    app.run(host='0.0.0.0', port=port)  # 本番環境用のhostとportを設定
