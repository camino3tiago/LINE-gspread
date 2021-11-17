# Herokuデプロイ用
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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    # 本番環境用
    port = os.getenv('PORT')    # Heroku上の環境変数PORTを取得
    app.run(host='0.0.0.0', port=port)  # 本番環境用のhostとportを設定
