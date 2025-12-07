import json
import os
from typing import Dict, Any
import urllib.request
import pymysql

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Обрабатывает webhook от Telegram бота: кнопки подтверждения/отклонения оплаты и команду /поиск
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        if 'message' in body_data:
            message = body_data['message']
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            
            if text.startswith('/поиск'):
                parts = text.split()
                if len(parts) < 2:
                    send_message(bot_token, chat_id, '❌ Использование: /поиск ник_игрока')
                else:
                    nickname = parts[1]
                    check_player_donate(bot_token, chat_id, nickname)
        
        elif 'callback_query' in body_data:
            callback = body_data['callback_query']
            callback_data = callback.get('data', '')
            callback_id = callback.get('id')
            chat_id = callback.get('message', {}).get('chat', {}).get('id')
            
            if callback_data.startswith('confirm_'):
                request_id = callback_data.replace('confirm_', '')
                confirm_payment_action(bot_token, callback_id, chat_id, request_id)
                
            elif callback_data.startswith('reject_'):
                request_id = callback_data.replace('reject_', '')
                reject_payment_action(bot_token, callback_id, chat_id, request_id)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def send_message(bot_token: str, chat_id: int, text: str):
    '''Отправляет сообщение в Telegram'''
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)


def check_player_donate(bot_token: str, chat_id: int, nickname: str):
    '''Проверяет баланс донат рублей игрока в базе SAMP'''
    try:
        conn = pymysql.connect(
            host=os.environ.get('SAMP_DB_HOST'),
            user=os.environ.get('SAMP_DB_USER'),
            password=os.environ.get('SAMP_DB_PASSWORD'),
            database=os.environ.get('SAMP_DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            table = os.environ.get('SAMP_DB_TABLE')
            nickname_col = os.environ.get('SAMP_NICKNAME_COLUMN')
            donate_col = os.environ.get('SAMP_DONATE_COLUMN')
            
            sql = f"SELECT {donate_col} FROM {table} WHERE {nickname_col} = '{nickname}'"
            cursor.execute(sql)
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            donate_amount = result[donate_col]
            message = f"👤 <b>Игрок:</b> {nickname}\n💰 <b>Донат рублей:</b> {donate_amount}"
            send_message(bot_token, chat_id, message)
        else:
            send_message(bot_token, chat_id, f'❌ Игрок с ником <b>{nickname}</b> не найден в базе')
    
    except Exception as e:
        send_message(bot_token, chat_id, f'❌ Ошибка при поиске: {str(e)}')


def confirm_payment_action(bot_token: str, callback_id: str, chat_id: int, request_id: str):
    '''Подтверждает оплату и начисляет донат рубли'''
    try:
        parts = request_id.split('_')
        nickname = parts[0]
        amount = int(parts[1])
        
        conn = pymysql.connect(
            host=os.environ.get('SAMP_DB_HOST'),
            user=os.environ.get('SAMP_DB_USER'),
            password=os.environ.get('SAMP_DB_PASSWORD'),
            database=os.environ.get('SAMP_DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            table = os.environ.get('SAMP_DB_TABLE')
            nickname_col = os.environ.get('SAMP_NICKNAME_COLUMN')
            donate_col = os.environ.get('SAMP_DONATE_COLUMN')
            
            sql = f"UPDATE {table} SET {donate_col} = {donate_col} + {amount} WHERE {nickname_col} = '{nickname}'"
            cursor.execute(sql)
            conn.commit()
        
        conn.close()
        
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_id,
            'text': '✅ Оплата подтверждена! Донат рубли начислены.'
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        
        send_message(bot_token, chat_id, f'✅ <b>Оплата подтверждена!</b>\n\n👤 Игрок: {nickname}\n💰 Начислено: {amount} донат рублей')
        
    except Exception as e:
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_id,
            'text': f'❌ Ошибка: {str(e)}'
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)


def reject_payment_action(bot_token: str, callback_id: str, chat_id: int, request_id: str):
    '''Отклоняет заявку на оплату'''
    try:
        parts = request_id.split('_')
        nickname = parts[0]
        amount = int(parts[1])
        
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_id,
            'text': '❌ Оплата отклонена'
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        
        send_message(bot_token, chat_id, f'❌ <b>Оплата отклонена</b>\n\n👤 Игрок: {nickname}\n💰 Сумма: {amount} донат рублей')
        
    except Exception as e:
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_id,
            'text': f'❌ Ошибка: {str(e)}'
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
