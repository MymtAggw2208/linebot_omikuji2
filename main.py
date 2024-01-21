import os
import base64, hashlib, hmac
import logging
import random

from flask import abort, jsonify

from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    StickerMessage, StickerSendMessage,
    TemplateSendMessage,ConfirmTemplate,MessageAction
)

omikuji = {0:[6325,10979924,'大吉！良いことあるかも？'],
            1:[11537,52002741,'中吉。いつも通りがいちばん'],
            2:[11537,52002745,'小吉。些細なことだってしあわせ'],
            3:[11537,52002754,'吉。平穏無事のありがたみ'],
            4:[6325,10979917,'末吉。ちょっとだけ気をつけて'],
            5:[11537,52002765,'凶。おとなしく過ごして']}


def main(request):
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
    channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

    line_bot_api = LineBotApi(channel_access_token)
    parser = WebhookParser(channel_secret)

    body = request.get_data(as_text=True)
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode()

    if signature != request.headers['X_LINE_SIGNATURE']:
        return abort(405)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return abort(405)

    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessage):
                if event.message.text == 'おみくじ':
                    line_bot_api.reply_message(
                        event.reply_token,
                        get_omikuji()
                    )
                else:
                    reply_data = []
                    if event.message.text == 'やめとく':
                        reply_data.append(
                            StickerSendMessage(
                                package_id=6325, sticker_id=10979923
                            ))
                    
                    reply_data.append(
                        make_button_template(event.message.text))
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_data
                    )
            else:
                continue

    return jsonify({ 'message': 'ok'})


def make_button_template(message_text):
    if message_text == 'やめとく':
        base_text = 'ほんとにひかない？'
    else:
        base_text = '『' + message_text + '』' + '\n おみくじひかない？'
    message_template = TemplateSendMessage(
        alt_text='おみくじ',
        template=ConfirmTemplate(
            text = base_text,            
            actions=[
                MessageAction(
                    text='おみくじ',
                    label='ひく'
                ),
                MessageAction(
                    text='やめとく',
                    label='ひかない'
                )
            ]
        )
    )
    return message_template


def get_omikuji():
    result = omikuji[random.randint(0,5)]
    sticker_message = StickerSendMessage(
        package_id=result[0], sticker_id=result[1]
    )
    text_message = TextSendMessage(text=result[2])
    return [sticker_message, text_message]
